import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FGISS.settings')
django.setup()

from StudentRecords.models import Student
from django.contrib.auth.models import User

def populate():
    print("Starting population...")
    
    # Create sample students based on your actual model fields
    students_data = [
        {
            'student_number': 'stu0001',
            'first_name': 'Maria',
            'last_name': 'Santos',
            'email': 'maria.santos@fgiss.edu',
            'phone_number': '09123456789',
            'dob': '2008-05-15',
            'date_of_enrollment': '2025-06-01',
            'grade_level': 'Grade 1',
            'section': '1-A',
            'is_active': True
        },
        {
            'student_number': 'stu0002',
            'first_name': 'John',
            'last_name': 'Reyes',
            'email': 'john.reyes@fgiss.edu',
            'phone_number': '09123456788',
            'dob': '2008-03-20',
            'date_of_enrollment': '2025-06-01',
            'grade_level': 'Grade 1',
            'section': '1-A',
            'is_active': True
        },
        {
            'student_number': 'stu0003',
            'first_name': 'Clara',
            'last_name': 'Dizon',
            'email': 'clara.dizon@fgiss.edu',
            'phone_number': '09123456787',
            'dob': '2008-08-10',
            'date_of_enrollment': '2025-06-01',
            'grade_level': 'Grade 2',
            'section': '2-A',
            'is_active': True
        }
    ]
    
    created_count = 0
    for data in students_data:
        student, created = Student.objects.get_or_create(
            student_number=data['student_number'],
            defaults=data
        )
        if created:
            created_count += 1
            print(f"✓ Created: {student.first_name} {student.last_name} ({student.student_number})")
        else:
            print(f"○ Already exists: {student.first_name} {student.last_name}")
    
    print(f"\n✅ Population complete! Created {created_count} new students.")
    print(f"📊 Total students in database: {Student.objects.count()}")

if __name__ == '__main__':
    populate()