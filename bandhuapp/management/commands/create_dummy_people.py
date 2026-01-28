"""
Django management command to create dummy data for People's page.
Based on actual website data from screenshots.

Usage:
    python manage.py create_dummy_people
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from bandhuapp.models import Profile, Staff, Designation, PeoplesDesignation
from datetime import date

class Command(BaseCommand):
    help = 'Creates dummy data for People\'s page based on actual website data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating dummy data for People\'s page...'))
        
        # Create or get "Core Team" designation
        designation, created = Designation.objects.get_or_create(
            title='Core Team',
            defaults={'rank': 1}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created designation: {designation.title}'))
        else:
            self.stdout.write(f'Using existing designation: {designation.title}')
        
        # Clear existing Core Team data to ensure only 8 people
        existing_peoples_designations = PeoplesDesignation.objects.filter(designation=designation)
        if existing_peoples_designations.exists():
            count = existing_peoples_designations.count()
            self.stdout.write(self.style.WARNING(f'Found {count} existing Core Team members. Deleting them...'))
            # Delete in reverse order to handle foreign key constraints
            for pd in existing_peoples_designations:
                staff = pd.staff
                profile = staff.profile
                user = profile.user
                pd.delete()  # Delete PeoplesDesignation first
                staff.delete()  # Delete Staff
                profile.delete()  # Delete Profile
                user.delete()  # Delete User
            self.stdout.write(self.style.SUCCESS(f'Cleared {count} existing Core Team members.'))
        
        # Dummy people data - 8 people with mix of males and females
        people_data = [
            {
                'first_name': 'Sanjeeb',
                'last_name': 'Mohapatra',
                'gender': 'M',
                'profession': 'Senior Solution Data Architect',
                'email': 'sanjeeb.mohapatra@example.com',
                'contact_no': '9876543210',
                'dob': date(1980, 1, 15),
            },
            {
                'first_name': 'Priyanka',
                'last_name': 'Das',
                'gender': 'F',
                'profession': 'Senior software engineer at Amazon, USA',
                'email': 'priyanka.das@example.com',
                'contact_no': '9876543211',
                'dob': date(1985, 3, 20),
            },
            {
                'first_name': 'Tarakanta',
                'last_name': 'Nayak',
                'gender': 'M',
                'profession': 'Teacher',
                'email': 'tarakanta.nayak@example.com',
                'contact_no': '9876543212',
                'dob': date(1975, 5, 10),
            },
            {
                'first_name': 'Snehalata',
                'last_name': 'Pattnaik',
                'gender': 'F',
                'profession': 'Govt Servant',
                'email': 'snehalata.pattnaik@example.com',
                'contact_no': '9876543213',
                'dob': date(1978, 7, 25),
            },
            {
                'first_name': 'Sudhanshu Mohan',
                'last_name': 'Rout',
                'gender': 'M',
                'profession': 'service',
                'email': 'sudhanshu.rout@example.com',
                'contact_no': '9876543214',
                'dob': date(1982, 9, 12),
            },
            {
                'first_name': 'Sraban',
                'last_name': 'Mohanty',
                'gender': 'M',
                'profession': 'Professor',
                'email': 'sraban.mohanty@example.com',
                'contact_no': '9876543216',
                'dob': date(1970, 4, 18),
            },
            {
                'first_name': 'Anjali',
                'last_name': 'Sahoo',
                'gender': 'F',
                'profession': 'Insurance advisor',
                'email': 'anjali.sahoo@example.com',
                'contact_no': '9876543217',
                'dob': date(1987, 6, 30),
            },
            {
                'first_name': 'Biswakam',
                'last_name': 'Mishra',
                'gender': 'M',
                'profession': 'IT Professional',
                'email': 'biswakam.mishra@example.com',
                'contact_no': '9876543218',
                'dob': date(1984, 8, 22),
            },
        ]
        
        created_count = 0
        skipped_count = 0
        
        for person_data in people_data:
            email = person_data.pop('email')
            
            # Check if user already exists
            user, user_created = User.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )
            
            if not user_created:
                self.stdout.write(self.style.WARNING(f'User {email} already exists, skipping...'))
                skipped_count += 1
                continue
            
            # Create profile
            profile = Profile.objects.create(
                user=user,
                first_name=person_data['first_name'],
                last_name=person_data['last_name'],
                gender=person_data['gender'],
                dob=person_data['dob'],
                contact_no=person_data['contact_no'],
                profession=person_data['profession'],
                street_address1='123 Main Street',
                street_address2='',
                city='Bhubaneswar',
                state='Odisha',
                pincode='751001',
                profile_pic=None  # Will use man.png/woman.png based on gender
            )
            
            # Create staff
            staff = Staff.objects.create(
                profile=profile,
                about=f'{person_data["first_name"]} {person_data["last_name"]} is a dedicated member of the Core Team, contributing significantly to the organization\'s mission and vision. With expertise in {person_data["profession"]}, they bring valuable experience and commitment to our cause.',
                webpage='',
                facebook='',
                twitter='',
                linkedin='',
                youtube=''
            )
            
            # Create people designation (OneToOne relationship)
            PeoplesDesignation.objects.create(
                staff=staff,
                designation=designation,
                desc=f'{person_data["first_name"]} {person_data["last_name"]} serves as {person_data["profession"]} in the Core Team, bringing years of experience and dedication to the organization.',
                rank=created_count + 1
            )
            
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'Created: {person_data["first_name"]} {person_data["last_name"]}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {created_count} people (8 total)'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'⚠️  Skipped {skipped_count} existing users'))
        self.stdout.write(self.style.SUCCESS('\nYou can now view the People\'s page at: http://127.0.0.1:8000/people/'))
