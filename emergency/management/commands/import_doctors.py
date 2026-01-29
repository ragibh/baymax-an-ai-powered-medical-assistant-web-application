import csv
import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from emergency.models import Doctor

class Command(BaseCommand):
    help = 'Import doctors from CSV file with data cleaning'
    
    def clean_text(self, text):
        """Clean and standardize text data"""
        if not text:
            return ''
        # Remove extra spaces, normalize case
        text = re.sub(r'\s+', ' ', text.strip())
        return text.title()
    
    def clean_phone(self, phone):
        """Clean phone number"""
        if not phone:
            return ''
        # Remove non-digit characters
        phone = re.sub(r'\D', '', phone)
        # Ensure it starts with country code if needed
        if phone and not phone.startswith('0') and not phone.startswith('880'):
            phone = '0' + phone
        return phone[:11]  # Keep to reasonable length
    
    def handle(self, *args, **options):
        csv_file_path = os.path.join(settings.BASE_DIR, 'data', 'bangladesh_doctors.csv')
        
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR('CSV file not found!'))
            return
        
        try:
            # Clear existing data (optional - remove if you want to keep existing)
            # Doctor.objects.all().delete()
            
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                doctors_created = 0
                doctors_updated = 0
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Clean the data
                        provider = self.clean_text(row.get('Provider', ''))
                        division = self.clean_text(row.get('Division', ''))
                        district = self.clean_text(row.get('District', ''))
                        upazila = self.clean_text(row.get('Upazila', ''))
                        department = self.clean_text(row.get('Department', ''))
                        contact_no = self.clean_phone(row.get('ContactNo', ''))
                        
                        # Skip if essential data is missing
                        if not provider or not division or not district:
                            self.stdout.write(
                                self.style.WARNING(f'Skipping row {row_num}: Missing essential data')
                            )
                            continue
                        
                        # Extract hospital name from address
                        address = self.clean_text(row.get('Address', ''))
                        hospital_name = address.split(',')[0] if address else ''
                        
                        # Create or update doctor
                        doctor, created = Doctor.objects.update_or_create(
                            provider=provider,
                            contact_no=contact_no,
                            defaults={
                                'post': self.clean_text(row.get('Post', '')),
                                'division': division,
                                'district': district,
                                'upazila': upazila,
                                'professional': self.clean_text(row.get('Professional', '')),
                                'address': address,
                                'degree': self.clean_text(row.get('Degree', '')),
                                'department': department,
                                'hospital_name': hospital_name,
                            }
                        )
                        
                        if created:
                            doctors_created += 1
                        else:
                            doctors_updated += 1
                            
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error processing row {row_num}: {str(e)}')
                        )
                        continue
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Successfully imported {doctors_created} new doctors! '
                        f'Updated {doctors_updated} existing doctors.'
                    )
                )
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error importing doctors: {str(e)}'))