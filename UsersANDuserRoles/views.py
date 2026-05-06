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

@csrf_protect
def login_check_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        if not email.endswith('@fgiss.edu'):
            return JsonResponse({'success': False, 'message': 'Please use your full @fgiss.edu email address to log in.'})
        
        password = request.POST.get('password')
        
        # Authenticate using database-level users
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            profile = getattr(user, 'profile', None)
            if profile and profile.role:
                role_name = profile.role.name.lower()
                
                # Determine user_type based on database role
                user_type = 'student'
                if role_name == 'admin': user_type = 'admin'
                elif 'teacher' in role_name: user_type = 'teacher'
                elif 'staff' in role_name: user_type = 'staff'
                elif 'guidance' in role_name: user_type = 'guidance'
                elif role_name == 'coordinator': user_type = 'coordinator'
                
                request.session['user_email'] = email
                request.session['user_type'] = user_type
                
                if user_type == 'admin':
                    return JsonResponse({'success': True, 'redirect_url': '/admin-dashboard/'})
                elif user_type == 'student':
                    student = Student.objects.filter(email=email).first()
                    if student:
                        request.session['student_id'] = student.id
                    return JsonResponse({'success': True, 'redirect_url': '/student/dashboard/'})
                elif user_type == 'guidance':
                    return JsonResponse({'success': True, 'redirect_url': '/intervention-plan/'})
                elif user_type == 'coordinator':
                    return JsonResponse({'success': True, 'redirect_url': '/incident-report/'})
                else:
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
            student_number=f"stu{User.objects.filter(email=user_email).first().id if User.objects.filter(email=user_email).first() else 1001}",
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
                # Use @fgiss.edu for all users
                target_domain = '@fgiss.edu'
                
                if '@' not in email:
                    full_email = f"{email}{target_domain}"
                else:
                    # If they typed an email, ensure it ends with @fgiss.edu
                    if not email.endswith(target_domain):
                        # Optionally force it or return error. Let's force it for consistency if it's missing the domain
                        prefix = email.split('@')[0]
                        full_email = f"{prefix}{target_domain}"
                    else:
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
                        email=full_email,
                        student_number=f"stu{user.id:04d}" # Generate a dummy student number
                    )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
            
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@csrf_exempt
def delete_user_view(request, user_id):
    if request.method == 'POST':
        # Check if user has permission (admin)
        if request.session.get('user_type') != 'admin':
            return JsonResponse({'success': False, 'message': 'Access denied.'})
            
        try:
            with transaction.atomic():
                user = get_object_or_404(User, id=user_id)
                email = user.email
                
                # If it's a student, also delete the Student record
                # We need to import Student inside if it's not at top level or use the already imported one
                from StudentRecords.models import Student
                Student.objects.filter(email=email).delete()
                
                # Delete the user (this will also delete the profile due to CASCADE)
                user.delete()
                
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