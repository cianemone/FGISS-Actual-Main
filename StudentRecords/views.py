import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib import messages
from django.db import models as django_models
from django.db.models import Count
from .models import Student
from .serializers import StudentSerializer

# REST API ViewSet
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().order_by('section', 'last_name', 'first_name')
    serializer_class = StudentSerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if query:
            students = Student.objects.filter(
                django_models.Q(student_number__icontains=query) |
                django_models.Q(first_name__icontains=query) |
                django_models.Q(last_name__icontains=query) |
                django_models.Q(email__icontains=query) |
                django_models.Q(section__icontains=query) |
                django_models.Q(grade_level__icontains=query)
            )
            serializer = self.get_serializer(students, many=True)
            return Response(serializer.data)
        return Response([])
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_students = Student.objects.count()
        active_students = Student.objects.filter(is_active=True).count()
        
        # Get section statistics
        section_stats = Student.objects.values('section').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_students': total_students,
            'active_students': active_students,
            'inactive_students': total_students - active_students,
            'sections': list(section_stats),
            'total_sections': section_stats.count(),
        })
    
    @action(detail=False, methods=['get'])
    def by_section(self, request):
        section = request.query_params.get('section', '')
        if section:
            students = Student.objects.filter(section=section, is_active=True)
            serializer = self.get_serializer(students, many=True)
            return Response(serializer.data)
        return Response([])

# Web Views with Filter System
def student_list_view(request):
    """Display list of students with filter options"""
    
    allowed_roles = ['staff', 'admin', 'coordinator']
    if request.session.get('user_type') not in allowed_roles:
        user_type = request.session.get('user_type')
        if user_type == 'student':
            user_email = request.session.get('user_email')
            student = Student.objects.filter(email=user_email).first()
            if student:
                return redirect('student_detail', student_number=student.student_number)
        return redirect('login')
    
    # Get filter parameters
    selected_section = request.GET.get('section', '')
    selected_grade = request.GET.get('grade', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    students = Student.objects.all().order_by('section', 'last_name', 'first_name')
    
    # Apply filters
    if selected_section:
        students = students.filter(section=selected_section)
    
    if selected_grade:
        students = students.filter(grade_level=selected_grade)
    
    if status_filter == 'active':
        students = students.filter(is_active=True)
    elif status_filter == 'inactive':
        students = students.filter(is_active=False)
    
    if search_query:
        students = students.filter(
            django_models.Q(student_number__icontains=search_query) |
            django_models.Q(first_name__icontains=search_query) |
            django_models.Q(last_name__icontains=search_query) |
            django_models.Q(email__icontains=search_query) |
            django_models.Q(phone_number__icontains=search_query)
        )
    
    # Get filter options
    sections = Student.objects.values_list('section', flat=True).distinct().exclude(section__isnull=True).exclude(section='').order_by('section')
    grade_levels = Student.objects.values_list('grade_level', flat=True).distinct().exclude(grade_level__isnull=True).exclude(grade_level='').order_by('grade_level')
    
    # Statistics by section
    section_counts = Student.objects.values('section').annotate(count=Count('id')).order_by('-count')
    
    # Summary
    total_students = Student.objects.count()
    active_students = Student.objects.filter(is_active=True).count()
    
    return render(request, 'student_list.html', {
        'students': students,
        'sections': sections,
        'grade_levels': grade_levels,
        'section_counts': section_counts,
        'selected_section': selected_section,
        'selected_grade': selected_grade,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_students': total_students,
        'active_students': active_students,
        'inactive_students': total_students - active_students,
        'filtered_count': students.count(),
    })

def student_form_view(request):
    """Add or edit student information"""
    
    allowed_roles = ['staff', 'admin', 'coordinator']
    if request.session.get('user_type') not in allowed_roles:
        return redirect('login')
    
    student_number = request.GET.get('student_number')
    student = None
    if student_number:
        student = get_object_or_404(Student, student_number=student_number)
    
    # Get existing sections for dropdown
    existing_sections = Student.objects.values_list('section', flat=True).distinct().exclude(section__isnull=True).exclude(section='').order_by('section')
    
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            if email and '@' not in email:
                email = f"{email}@fgiss.edu"
                data['email'] = email
            
            if student_number:
                # Update existing student
                student = get_object_or_404(Student, student_number=student_number)
                student.first_name = data.get('first_name')
                student.last_name = data.get('last_name')
                student.email = data.get('email')
                student.phone_number = data.get('phone_number')
                student.dob = data.get('dob') or None
                student.date_of_enrollment = data.get('date_of_enrollment') or None
                student.section = data.get('section')
                student.grade_level = data.get('grade_level')
                student.address = data.get('address')
                student.is_active = data.get('is_active', True)
                student.emergency_contact_name = data.get('emergency_contact_name')
                student.emergency_contact_phone = data.get('emergency_contact_phone')
                student.emergency_contact_relationship = data.get('emergency_contact_relationship')
                student.save()
                return JsonResponse({'status': 'success', 'message': 'Student updated successfully'})
            else:
                # Create new student
                student = Student.objects.create(
                    student_number=data.get('student_number'),
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    email=data.get('email'),
                    phone_number=data.get('phone_number'),
                    dob=data.get('dob') or None,
                    date_of_enrollment=data.get('date_of_enrollment') or None,
                    section=data.get('section'),
                    grade_level=data.get('grade_level'),
                    address=data.get('address'),
                    is_active=data.get('is_active', True),
                    emergency_contact_name=data.get('emergency_contact_name'),
                    emergency_contact_phone=data.get('emergency_contact_phone'),
                    emergency_contact_relationship=data.get('emergency_contact_relationship'),
                )
                return JsonResponse({'status': 'success', 'message': 'Student added successfully'})
        
        except Exception as e:
            # Return detailed error message for debugging
            import traceback
            error_details = {
                'status': 'error', 
                'message': str(e),
                'error_type': type(e).__name__,
                'traceback': traceback.format_exc()
            }
            print("=" * 50)
            print("ERROR SAVING STUDENT:")
            print(error_details)
            print("=" * 50)
            return JsonResponse(error_details, status=400)
    
    return render(request, 'student_form.html', {
        'student': student,
        'is_edit': bool(student_number),
        'existing_sections': existing_sections,
    })
def student_detail_view(request, student_number):
    """Display detailed information for a specific student"""
    
    student = get_object_or_404(Student, student_number=student_number)
    
    user_type = request.session.get('user_type')
    user_email = request.session.get('user_email')
    
    # Check if user is the student themselves
    is_owner = (user_type == 'student' and student.email == user_email)
    
    # Students can only view their own record
    if user_type == 'student' and not is_owner:
        messages.error(request, 'You can only view your own record.')
        return redirect('dashboard')
    
    # Get other students in same section
    same_section_students = Student.objects.filter(
        section=student.section, 
        is_active=True
    ).exclude(student_number=student.student_number)[:5] if student.section else []
    
    return render(request, 'student_detail.html', {
        'student': student,
        'same_section_students': same_section_students,
        'is_owner': is_owner,
        'user_type': user_type,
    })

def student_delete_view(request, student_number):
    """Delete a student record"""
    
    allowed_roles = ['staff', 'admin', 'coordinator']
    if request.session.get('user_type') not in allowed_roles:
        return redirect('login')
    
    student = get_object_or_404(Student, student_number=student_number)
    
    if request.method == "POST":
        student_name = f"{student.first_name} {student.last_name}"
        student.delete()
        messages.success(request, f'Student {student_name} has been deleted successfully.')
        return redirect('student_list')
    
    return render(request, 'student_confirm_delete.html', {'student': student})

def student_self_edit_view(request):
    """Allow students to edit their own contact information only"""
    
    # Check if user is logged in as student
    user_type = request.session.get('user_type')
    user_email = request.session.get('user_email')
    
    if user_type != 'student':
        messages.error(request, 'Access denied. Student portal only.')
        return redirect('login')
    
    # Get the student record using email from session
    student = get_object_or_404(Student, email=user_email)
    
    # Handle form submission
    if request.method == "POST":
        # Get editable fields
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        if email and '@' not in email:
            email = f"{email}@fgiss.edu"
        
        address = request.POST.get('address')
        emergency_contact_name = request.POST.get('emergency_contact_name')
        emergency_contact_phone = request.POST.get('emergency_contact_phone')
        emergency_contact_relationship = request.POST.get('emergency_contact_relationship')
        
        # Update only the editable fields
        if phone_number is not None:
            student.phone_number = phone_number
        if email and email != student.email:
            # Check if email is already used by another student
            if Student.objects.filter(email=email).exclude(id=student.id).exists():
                messages.error(request, 'This email is already used by another student.')
                return redirect('student_self_edit')
            student.email = email
            # Update session email
            request.session['user_email'] = email
        if address is not None:
            student.address = address
        if emergency_contact_name is not None:
            student.emergency_contact_name = emergency_contact_name
        if emergency_contact_phone is not None:
            student.emergency_contact_phone = emergency_contact_phone
        if emergency_contact_relationship is not None:
            student.emergency_contact_relationship = emergency_contact_relationship
        
        student.save()
        messages.success(request, 'Your information has been updated successfully!')
        return redirect('student_detail', student_number=student.student_number)
    
    return render(request, 'student_self_edit.html', {
        'student': student,
    })