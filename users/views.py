import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import UserRegisterForm
from .models import BloodDonationHistory, HealthVital, UserProfile

VITAL_CHART_KEYS = [
    ('bp_systolic', 'Blood Pressure (Systolic)'),
    ('bp_diastolic', 'Blood Pressure (Diastolic)'),
    ('glucose', 'Blood Glucose'),
    ('weight', 'Weight (kg)'),
    ('heart_rate', 'Heart Rate'),
]


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard:home')
        messages.error(request, 'Invalid username or password.')

    return render(request, 'users/login.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone') or '',
                address=form.cleaned_data.get('address') or '',
                age=form.cleaned_data.get('age'),
            )
            messages.success(request, 'Account created! You can sign in now.')
            return redirect('users:login')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    from predictions.models import Prediction
    from predictions.utils import get_user_health_dashboard

    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    health = get_user_health_dashboard(request.user)
    vitals = HealthVital.objects.filter(user=request.user).order_by('-recorded_at')
    donations = BloodDonationHistory.objects.filter(user=request.user)
    ml_predictions = Prediction.objects.filter(user=request.user).order_by('-created_at')[:50]

    preds = list(Prediction.objects.filter(user=request.user))
    if preds:
        clean = sum(1 for p in preds if 'No' in p.result or 'no' in p.result.lower() or 'Normal' in p.result)
        health_score = round((clean / len(preds)) * 100)
    else:
        health_score = None

    chart_data = {}
    for vt, _label in VITAL_CHART_KEYS:
        records = list(
            HealthVital.objects.filter(user=request.user, vital_type=vt).order_by('recorded_at')[:30]
        )
        chart_data[vt] = {
            'labels': [r.recorded_at.strftime('%b %d') for r in records],
            'values': [r.value for r in records],
        }

    return render(request, 'users/profile.html', {
        'profile': profile_obj,
        'health': health,
        'vitals': vitals[:20],
        'donations': donations,
        'chart_data': json.dumps(chart_data),
        'vital_types': HealthVital.VITAL_TYPES,
        'vital_chart_keys': VITAL_CHART_KEYS,
        'ml_predictions': ml_predictions,
        'health_score': health_score,
    })


@login_required
def update_profile(request):
    if request.method == 'POST':
        profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
        profile_obj.phone = request.POST.get('phone', profile_obj.phone)
        profile_obj.address = request.POST.get('address', profile_obj.address)
        profile_obj.blood_group = request.POST.get('blood_group', profile_obj.blood_group)
        try:
            age_val = request.POST.get('age', '')
            profile_obj.age = int(age_val) if age_val else None
        except (ValueError, TypeError):
            pass
        if 'avatar' in request.FILES:
            profile_obj.avatar = request.FILES['avatar']
        profile_obj.save()
        messages.success(request, 'Profile updated!')
    return redirect('users:profile')


@login_required
def add_vital(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            recorded = data.get('recorded_at')
            if recorded:
                recorded_at = datetime.fromisoformat(recorded.replace('Z', '+00:00'))
                if timezone.is_naive(recorded_at):
                    recorded_at = timezone.make_aware(recorded_at)
            else:
                recorded_at = timezone.now()

            HealthVital.objects.create(
                user=request.user,
                vital_type=data['vital_type'],
                value=float(data['value']),
                note=data.get('note', ''),
                recorded_at=recorded_at,
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)


@login_required
def delete_vital(request, vital_id):
    if request.method == 'POST':
        HealthVital.objects.filter(id=vital_id, user=request.user).delete()
    return redirect('users:profile')


@login_required
def add_donation(request):
    if request.method == 'POST':
        try:
            BloodDonationHistory.objects.create(
                user=request.user,
                donated_at=request.POST['donated_at'],
                location=request.POST.get('location', ''),
                recipient_note=request.POST.get('recipient_note', ''),
                units=float(request.POST.get('units', 1.0)),
            )
            messages.success(request, 'Donation record added!')
        except Exception as e:
            messages.error(request, str(e))
    return redirect('users:profile')
