import os
import django
from datetime import date, datetime, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FGISS.settings')
django.setup()

from django.contrib.auth.models import User
from UsersANDuserRoles.models import Role, UserProfile
from StudentRecords.models import Student
from StudentGrades.models import Subject, Grade
from StudentBehaviour.models import BehaviourIncident, InterventionPlan
from ClassSchedules.models import ClassSchedule
from CourseSyllabi.models import Syllabus
from ExamSchedules.models import ExamSchedule
from ExamCoverage.models import ExamCoverage

def sync():
    print("--- Starting Full Database Synchronization ---")

    # 1. Create Roles
    print("Syncing Roles...")
    roles_data = [
        (1, 'Student'),
        (2, 'Admin'),
        (3, 'Teacher'),
        (4, 'Coordinator'),
        (5, 'Guidance Counselor')
    ]
    for rid, name in roles_data:
        Role.objects.get_or_create(id=rid, defaults={'name': name})

    # 2. Sync Subjects
    subjects_data = {
        '1-3': ["Reading and Literacy", "Language", "Mathematics", "Science", "Filipino", "Makabansa", "EKAWP", "Arabic and Islam", "Co-Curricular"],
        '4-5': ["English", "Mathematics", "Science", "Filipino", "Civics and Culture", "MAPEH", "EKAWP", "HELE", "Arabic and Islam", "Co-Curricular"],
        '6': ["English", "Mathematics", "Science", "Filipino", "Civics and Culture", "MAPEH", "EKAWP", "HELE", "Pre-Algebra", "Arabic and Islam", "Co-Curricular"]
    }

    print("Syncing Subjects...")
    for grade_num in range(1, 7):
        grade_str = f"Grade {grade_num}"
        if grade_num <= 3:
            list_to_use = subjects_data['1-3']
        elif grade_num <= 5:
            list_to_use = subjects_data['4-5']
        else:
            list_to_use = subjects_data['6']
            
        for index, sub_name in enumerate(list_to_use):
            Subject.objects.update_or_create(
                name=sub_name, 
                grade_level=grade_str,
                defaults={'order': index}
            )

    # 3. Create Syllabi
    print("Syncing Syllabi...")
    syllabi_list = [
        ("MATH101", "Basic Mathematics", "Foundations of arithmetic.", "Addition, Subtraction, Numbers 1-100"),
        ("ENG401", "Intermediate English", "Grammar and composition.", "Parts of speech, Sentence structure"),
        ("SCI601", "Advanced Science", "Physics and Biology basics.", "The Cell, Simple Machines"),
    ]
    for code, title, desc, topics in syllabi_list:
        Syllabus.objects.update_or_create(course_code=code, defaults={'title': title, 'description': desc, 'topics': topics})

    # 4. Create Students and Users
    students_data = [
        {
            'full_name': 'Juan Dela Cruz',
            'email': 'juan.delacruz@fgiss.edu',
            'grade_level': 'Grade 1',
            'section': '1-A',
            'dob': '2018-05-15',
            'phone': '09123456781'
        },
        {
            'full_name': 'Maria Santos',
            'email': 'maria@fgiss.edu',
            'grade_level': 'Grade 4',
            'section': '4-B',
            'dob': '2015-03-20',
            'phone': '09123456782'
        },
        {
            'full_name': 'Carlos Reyes',
            'email': 'carlos@fgiss.edu',
            'grade_level': 'Grade 6',
            'section': '6-A',
            'dob': '2013-08-10',
            'phone': '09123456783'
        },
        {
            'full_name': 'John Reyes',
            'email': 'john.reyes@fgiss.edu',
            'grade_level': 'Grade 1',
            'section': '1-A',
            'dob': '2018-03-20',
            'phone': '09123456784'
        },
        {
            'full_name': 'Clara Dizon',
            'email': 'clara.dizon@fgiss.edu',
            'grade_level': 'Grade 2',
            'section': '2-A',
            'dob': '2017-11-12',
            'phone': '09123456785'
        }
    ]

    print("Syncing Students...")
    for s in students_data:
        first_name, last_name = s['full_name'].split(' ', 1)
        user, created = User.objects.get_or_create(
            username=s['email'],
            defaults={'email': s['email'], 'first_name': first_name, 'last_name': last_name}
        )
        if created:
            user.set_password('pass123')
            user.save()

        UserProfile.objects.get_or_create(user=user, defaults={'role': Role.objects.get(id=1), 'phone': s['phone']})
        
        student, _ = Student.objects.update_or_create(
            email=s['email'],
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'student_number': f"stu{user.id:04d}",
                'grade_level': s['grade_level'],
                'section': s['section'],
                'dob': s['dob'],
                'phone_number': s['phone'],
                'date_of_enrollment': date(2025, 6, 1)
            }
        )

        # 5. Add Grades for this student
        subjects = Subject.objects.filter(grade_level=s['grade_level'])[:3]
        for sub in subjects:
            Grade.objects.update_or_create(
                student=student, subject=sub, term="First Quarter",
                defaults={'score': 85.0, 'remarks': 'Great progress!'}
            )

        # 6. Add Intervention Plan for some students
        if s['email'] == 'juan.delacruz@fgiss.edu':
            InterventionPlan.objects.update_or_create(
                student=student,
                defaults={
                    'intervention_type': 'Academic Support',
                    'start_date': date(2026, 1, 1),
                    'review_date': date(2026, 6, 1),
                    'primary_goal': 'Improve reading comprehension to grade level.'
                }
            )

    # 7. Create Staff Users
    staff_data = [
        ('Teacher One', 'teacher1@fgiss.edu', 3),
        ('Admin User', 'admin@fgiss.edu', 2),
        ('Counselor User', 'counselor@fgiss.edu', 5),
        ('Coordinator User', 'coordinator@fgiss.edu', 4),
    ]

    print("Syncing Staff...")
    for name, email, role_id in staff_data:
        first, last = name.split(' ', 1)
        user, created = User.objects.get_or_create(
            username=email,
            defaults={'email': email, 'first_name': first, 'last_name': last}
        )
        if created:
            user.set_password('pass123')
            user.save()
        UserProfile.objects.get_or_create(user=user, defaults={'role': Role.objects.get(id=role_id)})

    # 8. Create Class Schedules
    print("Syncing Schedules...")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    sections = ["1-A", "2-A", "4-B", "6-A"]
    
    for section in sections:
        g_level = f"Grade {section[0]}"
        subjects = Subject.objects.filter(grade_level=g_level)[:3]
        for i, sub in enumerate(subjects):
            day = days[i % 5]
            sched, _ = ClassSchedule.objects.update_or_create(
                subject=sub, section=section, day_of_week=day,
                defaults={
                    'teacher_name': 'Mrs. Smith',
                    'start_time': time(8 + i, 0),
                    'end_time': time(9 + i, 0),
                    'room': f'Room {section}'
                }
            )
            
            # 9. Create Exam Schedules and Coverage
            exam, _ = ExamSchedule.objects.update_or_create(
                name=f"Midterm - {sub.name}", class_schedule=sched,
                defaults={'date': date(2026, 7, 15), 'start_time': time(9, 0), 'end_time': time(11, 0), 'room': sched.room}
            )
            
            syllabus = Syllabus.objects.first()
            if syllabus:
                ExamCoverage.objects.update_or_create(
                    exam=exam,
                    defaults={'syllabus': syllabus, 'topics_covered': 'Chapters 1-3', 'notes': 'Bring calculator.'}
                )

    print("\n--- Synchronization Complete! ---")

if __name__ == '__main__':
    sync()
