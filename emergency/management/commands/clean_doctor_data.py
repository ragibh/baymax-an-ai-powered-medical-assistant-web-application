from django.core.management.base import BaseCommand
from emergency.models import Doctor
import re

class Command(BaseCommand):
    help = 'Clean and standardize existing doctor data'
    
    def clean_field(self, field_value):
        """Clean a single field"""
        if not field_value:
            return field_value
        
        # Remove extra spaces
        field_value = re.sub(r'\s+', ' ', field_value.strip())
        
        # Standardize case for certain fields
        if field_value and field_value.isupper():
            field_value = field_value.title()
            
        return field_value
    
    def handle(self, *args, **options):
        doctors = Doctor.objects.all()
        updated_count = 0
        
        for doctor in doctors:
            original_division = doctor.division
            original_district = doctor.district
            original_department = doctor.department
            
            # Clean the fields
            doctor.division = self.clean_field(doctor.division)
            doctor.district = self.clean_field(doctor.district)
            doctor.department = self.clean_field(doctor.department)
            doctor.provider = self.clean_field(doctor.provider)
            doctor.upazila = self.clean_field(doctor.upazila)
            
            # Check if any field changed
            if (original_division != doctor.division or 
                original_district != doctor.district or 
                original_department != doctor.department):
                
                doctor.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Cleaned: {doctor.provider} - {doctor.division}, {doctor.district}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Successfully cleaned {updated_count} doctor records')
        )