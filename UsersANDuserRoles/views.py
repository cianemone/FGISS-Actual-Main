import json
from django.shortcuts import render, redirect
from rest_framework import viewsets
from django.contrib.auth.models import User
from .models import Role, UserProfile
from .serializers import UserSerializer, RoleSerializer, UserProfileSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages  # Add this import

from StudentRecords.models import Student

# Valid student accounts 
VALID_STUDENTS = {
    'juan@student.com': 'pass123',
    'maria@student.com': 'pass123',
    'carlos@student.com': 'pass123',
    'john@email.com': 'hashed_pw_1',
    'maria@email.com': 'hashed_pw_2',
    'clara@email.com': 'hashed_pw_3',
}

# FIXED: Added roles to the mock data to prevent privilege escalation
VALID_STAFF = {
    'teacher1@school.com': {'password': 'pass123', 'role': 'staff'},
    'admin@school.com': {'password': 'pass123', 'role': 'admin'},
    'counselor@school.com': {'password': 'pass123', 'role': 'guidance'},
    'coordinator@school.com': {'password': 'pass123', 'role': 'coordinator'},
    'mr.cruz@email.com': {'password': 'hashed_pw_staff1', 'role': 'staff'},
    'ms.reyes@email.com': {'password': 'hashed_pw_staff2', 'role': 'staff'},
    'mr.santos@email.com': {'password': 'hashed_pw_staff3', 'role': 'staff'},
    'admin.staff@email.com': {'password': 'hashed_pw_staff4', 'role': 'admin'},
}

@csrf_protect
def login_check_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')
        
        # 1. Try database-level authentication first
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            profile = getattr(user, 'profile', None)
            if profile and profile.role:
                role_name = profile.role.name.lower()
                
                # Determine user_type based on database role
                user_type = 'student'
                if role_name == 'admin': user_type = 'admin'
                elif role_name == 'teacher': user_type = 'staff'
                elif role_name == 'guidance counselor': user_type = 'guidance'
                elif role_name == 'coordinator': user_type = 'coordinator'
                
                request.session['user_email'] = email
                request.session['user_type'] = user_type
                
                if user_type == 'admin':
                    return JsonResponse({'success': True, 'redirect_url': '/admin-dashboard/'})
                elif user_type == 'student':
                    student = Student.objects.filter(email=email).first()
                    if student:
                        request.session['student_id'] = student.id
                    # CHANGE THIS - Redirect to student dashboard instead of report-cards
                    return JsonResponse({'success': True, 'redirect_url': '/student/dashboard/'})
                elif user_type == 'guidance':
                    return JsonResponse({'success': True, 'redirect_url': '/intervention-plan/'})
                else:
                    return JsonResponse({'success': True, 'redirect_url': '/edit-report-cards/'})

        # 2. Fallback to hardcoded dicts for existing dummy data
        # Detect role from email domain or specific email for hardcoded data
        detected_role = None
        if email in VALID_STUDENTS:
            detected_role = 'student'
        elif email in VALID_STAFF:
            detected_role = VALID_STAFF[email]['role']
            
        if detected_role == 'student':
            if VALID_STUDENTS.get(email) == password:
                request.session['user_email'] = email
                request.session['user_type'] = 'student'
                student = Student.objects.filter(email=email).first()
                if student:
                    request.session['student_id'] = student.id
                # CHANGE THIS - Redirect to student dashboard
                return JsonResponse({'success': True, 'redirect_url': '/student/dashboard/'})
                
        elif detected_role in ['staff', 'admin', 'coordinator', 'guidance']:
            staff_record = VALID_STAFF[email]
            if staff_record['password'] == password:
                request.session['user_email'] = email
                request.session['user_type'] = detected_role
                
                if detected_role == 'admin':
                    return JsonResponse({'success': True, 'redirect_url': '/admin-dashboard/'})
                elif detected_role == 'guidance':
                    return JsonResponse({'success': True, 'redirect_url': '/intervention-plan/'})
                return JsonResponse({'success': True, 'redirect_url': '/edit-report-cards/'})

        return JsonResponse({'success': False, 'message': 'Invalid email or password.'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def admin_dashboard_view(request):
    # Check if user has permission (admin)
    if request.session.get('user_type') != 'admin':
        return redirect('login')
    
    email = request.session.get('user_email')
    user = User.objects.filter(email=email).first()
    
    user_name = email
    if user and user.get_full_name():
        user_name = user.get_full_name()
    elif user:
        user_name = user.username
    
    return render(request, 'admin_dashboard.html', {
        'user_name': user_name,
        'user_email': email
    })

def user_roles_view(request):
    # Check if user has permission (admin)
    if request.session.get('user_type') != 'admin':
        return redirect('login')
    
    email = request.session.get('user_email')
    
    # Get all users with their profiles and roles
    users = User.objects.select_related('profile', 'profile__role').all()
    
    return render(request, 'user_roles.html', {
        'user_email': email,
        'db_users': users
    })

def student_dashboard_view(request):
    """Student dashboard - view only access to schedule and syllabus"""
    
    # Check if user is a student
    user_type = request.session.get('user_type')
    user_email = request.session.get('user_email')
    
    print(f"Debug - User Type: {user_type}, User Email: {user_email}")  # Debug print
    
    if user_type != 'student':
        messages.error(request, 'Access denied. Student portal only.')
        return redirect('login')
    
    # Get the student record
    from StudentRecords.models import Student
    
    try:
        student = Student.objects.get(email=user_email)
    except Student.DoesNotExist:
        # If student doesn't exist in database, create one from session data
        print(f"Student not found for email: {user_email}. Creating...")
        
        # Split email to get name (e.g., john@email.com -> John)
        name_part = user_email.split('@')[0]
        
        student = Student.objects.create(
            student_number=f"STU{User.objects.filter(email=user_email).first().id if User.objects.filter(email=user_email).first() else 1001}",
            first_name=name_part.capitalize(),
            last_name="Student",
            email=user_email,
            is_active=True
        )
        messages.info(request, 'Your student profile has been created.')
    
    return render(request, 'student_dashboard.html', {
        'student': student,
    })

@csrf_exempt
def create_user_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            role_name = data.get('role')
            
            if not all([name, email, password, role_name]):
                return JsonResponse({'success': False, 'message': 'All fields are required.'})
                
            with transaction.atomic():
                # Append role-based domain if not present
                domain_map = {
                    'student': '@student',
                    'admin': '@admin',
                    'teacher': '@staff',
                    'guidance counselor': '@guidance',
                    'coordinator': '@coordinator'
                }
                
                target_domain = domain_map.get(role_name.lower(), '@user')
                if '@' not in email:
                    full_email = f"{email}{target_domain}"
                else:
                    # If they typed an email, we ensure it has the right suffix or keep as is
                    full_email = email

                if User.objects.filter(username=full_email).exists() or User.objects.filter(email=full_email).exists():
                    return JsonResponse({'success': False, 'message': 'User with this email already exists.'})

                # Create the user
                user = User.objects.create_user(username=full_email, email=full_email, password=password)
                
                # Set first and last name if possible
                name_parts = name.split(' ', 1)
                user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = name_parts[1]
                user.save()
                
                # Get or create the role
                role, _ = Role.objects.get_or_create(name=role_name)
                
                # Create the profile
                UserProfile.objects.create(user=user, role=role)
                
                # If it's a student, also create a Student record
                if role_name.lower() == 'student':
                    Student.objects.create(
                        first_name=user.first_name,
                        last_name=user.last_name,
                        email=email,
                        student_number=f"STU{user.id:04d}" # Generate a dummy student number
                    )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
            
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def logout_view(request):
    request.session.flush()
    return redirect('login')

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by("username")
    serializer_class = UserSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related("user", "role")
    serializer_class = UserProfileSerializer