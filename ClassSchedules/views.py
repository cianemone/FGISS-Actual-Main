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
    elif user_type in ['admin', 'staff', 'teacher']:
        if query_section:
            schedules = schedules.filter(section=query_section)
        if query_grade:
            schedules = schedules.filter(subject__grade_level=query_grade)
    else:
        return redirect('login')

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
    if request.session.get('user_type') not in ['admin', 'staff', 'teacher']:
        return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            schedule_id = data.get('id')
            subject_id = data.get('subject_id')
            
            day_of_week = data.get('day_of_week')
            start_time_str = data.get('start_time')
            end_time_str = data.get('end_time')
            room = data.get('room')

            if not subject_id:
                return JsonResponse({'status': 'error', 'message': 'Subject is required.'})
            
            if not all([day_of_week, start_time_str, end_time_str]):
                return JsonResponse({'status': 'error', 'message': 'Missing required fields.'})

            # Check for conflicts with other ClassSchedules
            from django.db.models import Q
            
            section = data.get('section')
            teacher_name = data.get('teacher_name')
            
            # Base conflict query: same day and overlapping time
            base_conflict_query = Q(
                day_of_week=day_of_week,
                start_time__lt=end_time_str,
                end_time__gt=start_time_str
            )
            
            # Room conflict (only if room is specified)
            room_conflict = Q()
            if room:
                room_conflict = Q(room=room)
                
            # Teacher conflict (only if teacher is specified)
            teacher_conflict = Q()
            if teacher_name:
                teacher_conflict = Q(teacher_name=teacher_name)
                
            # Section conflict (only if section is specified)
            section_conflict = Q()
            if section:
                section_conflict = Q(section=section)
                
            # Combine them: Conflict if room, teacher, OR section overlaps
            conflict_filters = Q()
            if room:
                conflict_filters |= room_conflict
            if teacher_name:
                conflict_filters |= teacher_conflict
            if section:
                conflict_filters |= section_conflict
                
            class_conflicts = ClassSchedule.objects.filter(base_conflict_query & conflict_filters)

            if schedule_id:
                class_conflicts = class_conflicts.exclude(id=schedule_id)
            
            if class_conflicts.exists():
                conflict = class_conflicts.first()
                conflict_type = ""
                if room and conflict.room == room:
                    conflict_type = f"Room {room} is already occupied"
                elif teacher_name and conflict.teacher_name == teacher_name:
                    conflict_type = f"Teacher {teacher_name} is already busy"
                elif section and conflict.section == section:
                    conflict_type = f"Section {section} already has a class"
                
                return JsonResponse({
                    'status': 'error', 
                    'message': f"Conflict: {conflict_type} by '{conflict.subject.name if conflict.subject else 'Unnamed'}' on {day_of_week}s from {conflict.start_time} to {conflict.end_time}."
                })

            # Check for conflicts with ExamSchedules
            from ExamSchedules.models import ExamSchedule
            days = {
                'Sunday': 1, 'Monday': 2, 'Tuesday': 3, 'Wednesday': 4,
                'Thursday': 5, 'Friday': 6, 'Saturday': 7
            }
            weekday_num = days.get(day_of_week)
            
            exam_conflicts = ExamSchedule.objects.filter(
                start_time__lt=end_time_str,
                end_time__gt=start_time_str
            )
            
            if weekday_num:
                exam_conflicts = exam_conflicts.filter(date__week_day=weekday_num)

            # For exams, we mainly care about room and section conflicts
            # (Teacher info might not be directly in ExamSchedule model, but let's check room and section)
            exam_conflict_filters = Q()
            if room:
                exam_conflict_filters |= Q(room=room)
            if section:
                exam_conflict_filters |= Q(class_schedule__section=section)
                
            exam_conflicts = exam_conflicts.filter(exam_conflict_filters)

            if exam_conflicts.exists():
                conflict = exam_conflicts.first()
                conflict_type = ""
                if room and conflict.room == room:
                    conflict_type = f"Room {room} is reserved for an exam"
                elif section and conflict.class_schedule and conflict.class_schedule.section == section:
                    conflict_type = f"Section {section} has an exam"
                    
                return JsonResponse({
                    'status': 'error', 
                    'message': f"Conflict: {conflict_type} '{conflict.name}' scheduled on {conflict.date} (a {day_of_week}) from {conflict.start_time} to {conflict.end_time}."
                })

            if schedule_id:
                schedule = get_object_or_404(ClassSchedule, id=schedule_id)
            else:
                schedule = ClassSchedule()
            
            schedule.subject = get_object_or_404(Subject, id=subject_id)
            schedule.section = data.get('section')
            schedule.teacher_name = data.get('teacher_name')
            schedule.day_of_week = day_of_week
            schedule.start_time = start_time_str
            schedule.end_time = end_time_str
            schedule.room = room
            schedule.save()
            
            return JsonResponse({'status': 'success', 'message': 'Schedule saved successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def delete_class_schedule(request, schedule_id):
    if request.session.get('user_type') not in ['admin', 'staff', 'teacher']:
        return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)

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
