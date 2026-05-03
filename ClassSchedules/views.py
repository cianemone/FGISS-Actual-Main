from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from rest_framework import viewsets
from .models import ClassSchedule
from StudentGrades.models import Subject
from .serializers import ClassScheduleSerializer
from django.views.decorators.csrf import csrf_exempt
from StudentRecords.models import Student
import json

def class_schedule_view(request):
    # Check if user has permission
    user_type = request.session.get('user_type')
    user_email = request.session.get('user_email')
    
    if not user_type:
        return redirect('login')
    
    query_section = request.GET.get('section')
    query_grade = request.GET.get('grade')
    
    schedules = ClassSchedule.objects.all().order_by('day_of_week', 'start_time')
    
    student = None
    if user_type == 'student':
        student = Student.objects.filter(email=user_email).first()
        if student:
            if student.grade_level:
                schedules = schedules.filter(subject__grade_level=student.grade_level)
            if student.section:
                schedules = schedules.filter(section=student.section)
    else:
        if query_section:
            schedules = schedules.filter(section=query_section)
        if query_grade:
            schedules = schedules.filter(subject__grade_level=query_grade)

    # Get unique sections for the filter and dropdown
    # Combine sections from both existing schedules and defined student sections
    schedule_sections = ClassSchedule.objects.exclude(section__isnull=True).exclude(section='').values_list('section', flat=True).distinct()
    student_sections = Student.objects.exclude(section__isnull=True).exclude(section='').values_list('section', flat=True).distinct()
    
    unique_sections = sorted(list(set(list(schedule_sections) + list(student_sections))))
    
    subjects = Subject.objects.all().order_by('grade_level', 'order', 'name')
    grade_levels = [g[0] for g in Subject.GRADE_CHOICES]
    
    return render(request, 'class_schedule.html', {
        'schedules': schedules,
        'subjects': subjects,
        'unique_sections': unique_sections,
        'grade_levels': grade_levels,
        'current_section': query_section,
        'current_grade': query_grade,
        'user_email': user_email,
        'user_type': user_type,
        'is_admin_or_staff': user_type in ['admin', 'staff', 'teacher'],
        'student': student
    })

@csrf_exempt
def save_class_schedule(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            schedule_id = data.get('id')
            subject_id = data.get('subject_id')
            
            if not subject_id:
                return JsonResponse({'status': 'error', 'message': 'Subject is required.'})
                
            if schedule_id:
                schedule = get_object_or_404(ClassSchedule, id=schedule_id)
            else:
                schedule = ClassSchedule()
            
            schedule.subject = get_object_or_404(Subject, id=subject_id)
            schedule.section = data.get('section')
            schedule.teacher_name = data.get('teacher_name')
            schedule.day_of_week = data.get('day_of_week')
            schedule.start_time = data.get('start_time')
            schedule.end_time = data.get('end_time')
            schedule.room = data.get('room')
            schedule.save()
            
            return JsonResponse({'status': 'success', 'message': 'Schedule saved successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def delete_class_schedule(request, schedule_id):
    if request.method == 'POST':
        try:
            schedule = get_object_or_404(ClassSchedule, id=schedule_id)
            schedule.delete()
            return JsonResponse({'status': 'success', 'message': 'Schedule deleted successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

class ClassScheduleViewSet(viewsets.ModelViewSet):
    queryset = ClassSchedule.objects.all()
    serializer_class = ClassScheduleSerializer
