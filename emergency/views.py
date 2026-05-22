from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json
from .models import ChatMessage, EmergencyContact, Doctor
from .gemini_service import gemini_service
import uuid
import time

@login_required
def home(request):
    """Fast homepage with minimal database queries"""
    contacts = EmergencyContact.objects.all()[:6]  # Limit contacts for speed
    recent_messages = ChatMessage.objects.filter(user=request.user).order_by('-timestamp')[:5]  # Limit messages
    
    gemini_status = "✅ Online" if gemini_service.setup_complete else "🔧 Basic Mode"
    model_info = getattr(gemini_service, 'model_name', 'Unknown')
    
    return render(request, 'emergency/home.html', {
        'contacts': contacts,
        'recent_messages': reversed(list(recent_messages)),
        'gemini_status': gemini_status,
        'response_time': '⚡ Ultra Fast',
        'model_info': model_info
    })

@login_required
@csrf_exempt
def chatbot_api(request):
    """Optimized chatbot API with timeout"""
    if request.method == 'POST':
        start_time = time.time()
        
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()[:500]  # Limit message length
            session_id = data.get('session_id', f"{request.user.id}_{int(time.time())}")
            
            if not user_message:
                return JsonResponse({'error': 'Empty message'}, status=400)
            
            # Get Blobax response (with potential timeout in service)
            blobax_response = gemini_service.chat(user_message)
            
            ChatMessage.objects.create(
                user=request.user,
                message=user_message,
                response=blobax_response,
                is_user=True,
                session_id=session_id,
            )
            
            response_time = round(time.time() - start_time, 2)
            
            return JsonResponse({
                'response': blobax_response,
                'session_id': session_id,
                'response_time': response_time,
                'timestamp': int(time.time())
            })
            
        except Exception as e:
            return JsonResponse({
                'error': 'Server busy',
                'response': "I'm helping others right now. Please try again in a moment! 🩺❤️"
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def get_chat_history(request):
    """Fast chat history"""
    session_id = request.GET.get('session_id', '')
    messages = ChatMessage.objects.filter(
        user=request.user, 
        session_id=session_id
    ).order_by('-timestamp')[:10]  # Limit history
    
    chat_data = []
    for msg in messages:
        if msg.message:
            chat_data.append({
                'is_user': True,
                'message': msg.message,
                'timestamp': msg.timestamp.isoformat(),
            })
        if msg.response:
            chat_data.append({
                'is_user': False,
                'message': msg.response,
                'timestamp': msg.timestamp.isoformat(),
            })

    return JsonResponse({'messages': chat_data})

@login_required
@csrf_exempt
def clear_chat(request):
    """Clear all chat messages for the user"""
    if request.method == 'POST':
        try:
            # Delete all messages for this user
            deleted_count = ChatMessage.objects.filter(user=request.user).delete()[0]
            return JsonResponse({
                'success': True,
                'message': f'Cleared {deleted_count} messages',
                'deleted_count': deleted_count
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def emergency_directory(request):
    """Advanced doctor directory with filters - FIXED"""
    # Get filter parameters
    division = request.GET.get('division', '')
    district = request.GET.get('district', '')
    department = request.GET.get('department', '')
    search = request.GET.get('search', '')
    
    # Start with all doctors
    doctors = Doctor.objects.all()
    
    # Apply filters
    if division:
        doctors = doctors.filter(division__icontains=division)
    if district:
        doctors = doctors.filter(district__icontains=district)
    if department:
        doctors = doctors.filter(department__icontains=department)
    if search:
        doctors = doctors.filter(
            Q(provider__icontains=search) |
            Q(hospital_name__icontains=search) |
            Q(department__icontains=search) |
            Q(address__icontains=search)
        )
    
    # FIXED: Get UNIQUE values for filters (distinct only)
    divisions = Doctor.objects.values_list('division', flat=True).distinct().order_by('division')
    districts = Doctor.objects.values_list('district', flat=True).distinct().order_by('district')
    departments = Doctor.objects.values_list('department', flat=True).distinct().order_by('department')
    
    # FIXED: Count unique values properly
    total_unique_divisions = divisions.count()
    total_unique_districts = districts.count()
    total_unique_departments = departments.count()
    
    context = {
        'doctors': doctors,
        'divisions': divisions,
        'districts': districts,
        'departments': departments,
        'current_division': division,
        'current_district': district,
        'current_department': department,
        'current_search': search,
        'total_doctors': doctors.count(),
        'total_divisions': total_unique_divisions,
        'total_districts': total_unique_districts,
        'total_departments': total_unique_departments,
    }
    
    return render(request, 'emergency/directory.html', context)

@login_required
def get_doctor_details(request, doctor_id):
    """Get detailed doctor information for modal"""
    try:
        doctor = Doctor.objects.get(id=doctor_id)
        data = {
            'id': doctor.id,
            'provider': doctor.provider,
            'post': doctor.post,
            'division': doctor.division,
            'district': doctor.district,
            'upazila': doctor.upazila,
            'professional': doctor.professional,
            'contact_no': doctor.formatted_phone,
            'address': doctor.address,
            'degree': doctor.degree,
            'department': doctor.department,
            'hospital_name': doctor.hospital_name,
            'map_url': doctor.get_map_url(),
            'directions_url': doctor.get_directions_url(),
        }
        return JsonResponse(data)
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found'}, status=404)

@login_required
def get_filter_options(request):
    """Get filter options for AJAX filtering"""
    division = request.GET.get('division', '')
    
    if division:
        districts = Doctor.objects.filter(division=division).values_list('district', flat=True).distinct().order_by('district')
        departments = Doctor.objects.filter(division=division).values_list('department', flat=True).distinct().order_by('department')
    else:
        districts = Doctor.objects.values_list('district', flat=True).distinct().order_by('district')
        departments = Doctor.objects.values_list('department', flat=True).distinct().order_by('department')
    
    data = {
        'districts': list(districts),
        'departments': list(departments),
    }
    
    return JsonResponse(data)

# ADD THIS MISSING FUNCTION
@login_required
def check_status(request):
    """Check Gemini API status"""
    status = {
        'gemini_online': gemini_service.setup_complete,
        'model': getattr(gemini_service, 'model_name', 'Unknown'),
        'status': 'Operational' if gemini_service.setup_complete else 'Fallback Mode',
        'speed': 'Ultra Fast (Gemini 2.5)' if gemini_service.setup_complete else 'Basic Mode'
    }
    return JsonResponse(status)