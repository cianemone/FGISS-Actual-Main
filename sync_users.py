import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FGISS.settings')
django.setup()

from django.contrib.auth.models import User
from UsersANDuserRoles.models import Role, UserProfile
from StudentRecords.models import Student
from StudentGrades.models import Subject

def sync():
    roles_data = [
        (1, 'Student'),
        (2, 'Admin'),
        (3, 'Teacher'),
        (4, 'Coordinator'),
        (5, 'Guidance Counselor')
    ]
    for rid, name in roles_data:
        Role.objects.get_or_create(id=rid, defaults={'name': name})

    subjects_data = {
        '1-3': [
            "Reading and Literacy", 
            "Language", 
            "Mathematics", 
            "Science", 
            "Filipino", 
            "Makabansa", 
            "Good Manners and Right Conduct (Edukasyon sa Kagandahang Asal at Wastong Pag-uugali) EKAWP", 
            "Arabic and Islam Integration", 
            "Co-Curricular"
        ],
        '4-5': [
            "English", 
            "Mathematics", 
            "Science", 
            "Filipino", 
            "Civics and Culture (Sibika at Kultura)", 
            "Music, Art, Physical Education, and Health (Musika, Sining at Edukasyon sa Pagpapalakas ng Katawan) MAPEH", 
            "Good Manners and Right Conduct (Edukasyon sa Kagandahang Asal at Wastong Pag-uugali) EKAWP", 
            "HELE with Computer Integration", 
            "Arabic and Islam Integration", 
            "Co-Curricular"
        ],
        '6': [
            "English", 
            "Mathematics", 
            "Science", 
            "Filipino", 
            "Civics and Culture (Sibika at Kultura)", 
            "Music, Art, Physical Education, and Health (Musika, Sining at Edukasyon sa Pagpapalakas ng Katawan) MAPEH", 
            "Good Manners and Right Conduct (Edukasyon sa Kagandahang Asal at Wastong Pag-uugali) EKAWP", 
            "HELE with Computer Integration", 
            "Pre-Algebra", 
            "Arabic and Islam Integration", 
            "Co-Curricular"
        ]
    }

    print("Syncing Subjects with Order...")
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
    
    print("Subjects synced successfully.")

    students_data = [
        ('Juan Dela Cruz', 'juan@fgiss.edu', 'pass123', 1, 'Grade 1'),
        ('Maria Santos', 'maria@fgiss.edu', 'pass123', 1, 'Grade 4'),
        ('Carlos Reyes', 'carlos@fgiss.edu', 'pass123', 1, 'Grade 6'),
    ]

    for full_name, email, password, role_id, g_level in students_data:
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user, created = User.objects.get_or_create(
            username=email,
            defaults={'email': email, 'first_name': first_name, 'last_name': last_name}
        )
        if created:
            user.set_password(password)
            user.save()

        role = Role.objects.get(id=role_id)
        UserProfile.objects.get_or_create(user=user, defaults={'role': role})
        
        Student.objects.update_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'student_number': f"stu{user.id:04d}",
                'grade_level': g_level 
            }
        )
        print(f"Synced student: {email} to {g_level}")

    staff_data = [
        ('Mathematics Teacher', 'teacher1@fgiss.edu', 'pass123', 3),
        ('Administration', 'admin@fgiss.edu', 'pass123', 2),
        ('Guidance Counselor', 'counselor@fgiss.edu', 'pass123', 5),
        ('Coordinator User', 'coordinator@fgiss.edu', 'pass123', 4),
    ]

    for full_name, email, password, role_id in staff_data:
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user, created = User.objects.get_or_create(
            username=email,
            defaults={'email': email, 'first_name': first_name, 'last_name': last_name}
        )
        if created:
            user.set_password(password)
            user.save()

        role = Role.objects.get(id=role_id)
        UserProfile.objects.get_or_create(user=user, defaults={'role': role})
        print(f"Synced staff user: {email}")

if __name__ == '__main__':
    sync()