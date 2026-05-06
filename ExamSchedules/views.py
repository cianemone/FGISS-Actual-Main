from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from rest_framework import viewsets
from .models import ExamSchedule
from .serializers import ExamScheduleSerializer
from ClassSchedules.models import ClassSchedule
from ExamCoverage.models import ExamCoverage
from CourseSyllabi.models import Syllabus
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime

def exam_schedule_view(request):
    """Student view-only exam schedule"""
    user_type = request.session.get('user_type')
    if user_type != 'student':
        return redirect('login')
    
    from StudentRecords.models import Student
    student = Student.objects.filter(email=request.session.get('user_email')).first()
    
    if student and student.grade_level and student.section:
        exams = ExamSchedule.objects.filter(
            class_schedule__subject__grade_level=student.grade_level,
            class_schedule__section=student.section
        ).order_by('date', 'start_time')
    else:
        exams = ExamSchedule.objects.none()
    
    return render(request, 'exam_schedule.html', {
        'exams': exams,
        'user_email': request.session.get('user_email'),
        'student': student
    })

def edit_exam_schedule_view(request):
    """Admin/Teacher view with CRUD capabilities"""
    user_type = request.session.get('user_type')
    allowed_roles = ['admin', 'teacher']
    
    if user_type not in allowed_roles:
        return redirect('login')
    
    exams = ExamSchedule.objects.all().order_by('date', 'start_time')
    class_schedules = ClassSchedule.objects.all().order_by('subject__grade_level', 'section', 'subject__name')
    syllabi = Syllabus.objects.all().order_by('title')
    
    return render(request, 'edit_exam_schedule.html', {
        'exams': exams,
        'class_schedules': class_schedules,
        'syllabi': syllabi,
        'user_email': request.session.get('user_email')
    })

@csrf_exempt
def save_exam_schedule(request):
    if request.session.get('user_type') not in ['admin', 'teacher']:
        return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            exam_id = data.get('id')
            
            name = data.get('name')
            date_str = data.get('date')
            start_time_str = data.get('start_time')
            end_time_str = data.get('end_time')
            room = data.get('room')

            if not all([name, date_str, start_time_str, end_time_str]):
                return JsonResponse({'status': 'error', 'message': 'Missing required fields.'})

            # Check for conflicts with other ExamSchedules
            from django.db.models import Q
            
            class_sched_id = data.get('class_schedule_id')
            linked_class = None
            if class_sched_id:
                linked_class = get_object_or_404(ClassSchedule, id=class_sched_id)

            # Base conflict query: same date and overlapping time
            base_conflict_query = Q(
                date=date_str,
                start_time__lt=end_time_str,
                end_time__gt=start_time_str
            )
            
            # Conflict filters
            conflict_filters = Q()
            if room:
                conflict_filters |= Q(room=room)
            if linked_class and linked_class.section:
                conflict_filters |= Q(class_schedule__section=linked_class.section)
            
            exam_conflicts = ExamSchedule.objects.filter(base_conflict_query & conflict_filters)
            if exam_id:
                exam_conflicts = exam_conflicts.exclude(id=exam_id)
            
            if exam_conflicts.exists():
                conflict = exam_conflicts.first()
                conflict_type = ""
                if room and conflict.room == room:
                    conflict_type = f"Room {room} is already booked for another exam"
                elif linked_class and conflict.class_schedule and conflict.class_schedule.section == linked_class.section:
                    conflict_type = f"Section {linked_class.section} already has another exam"
                
                return JsonResponse({
                    'status': 'error', 
                    'message': f"Conflict: {conflict_type} '{conflict.name}' from {conflict.start_time} to {conflict.end_time} on {conflict.date}."
                })

            # Check for conflicts with ClassSchedules
            # Need to get day of week from date
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day_of_week = date_obj.strftime('%A')
            
            class_conflict_filters = Q()
            if room:
                class_conflict_filters |= Q(room=room)
            if linked_class and linked_class.section:
                class_conflict_filters |= Q(section=linked_class.section)
            if linked_class and linked_class.teacher_name:
                class_conflict_filters |= Q(teacher_name=linked_class.teacher_name)
                
            class_conflicts = ClassSchedule.objects.filter(
                day_of_week=day_of_week,
                start_time__lt=end_time_str,
                end_time__gt=start_time_str
            ).filter(class_conflict_filters)
            
            if class_conflicts.exists():
                conflict = class_conflicts.first()
                conflict_type = ""
                if room and conflict.room == room:
                    conflict_type = f"Room {room} has a regular class"
                elif linked_class and conflict.section == linked_class.section:
                    conflict_type = f"Section {linked_class.section} has a regular class"
                elif linked_class and conflict.teacher_name == linked_class.teacher_name:
                    conflict_type = f"Teacher {linked_class.teacher_name} has a regular class"
                    
                return JsonResponse({
                    'status': 'error', 
                    'message': f"Conflict: {conflict_type} '{conflict.subject.name if conflict.subject else 'Unnamed'}' on {day_of_week}s from {conflict.start_time} to {conflict.end_time}."
                })

            if exam_id:
                exam = get_object_or_404(ExamSchedule, id=exam_id)
            else:
                exam = ExamSchedule()
            
            exam.name = name
            class_sched_id = data.get('class_schedule_id')
            if class_sched_id:
                exam.class_schedule = get_object_or_404(ClassSchedule, id=class_sched_id)
            
            exam.date = date_str
            exam.start_time = start_time_str
            exam.end_time = end_time_str
            exam.room = room
            exam.save()

            # Handle Exam Coverage
            topics_covered = data.get('topics_covered', '')
            notes = data.get('notes', '')
            syllabus_id = data.get('syllabus_id')
            
            coverage, created = ExamCoverage.objects.get_or_create(exam=exam)
            coverage.topics_covered = topics_covered
            coverage.notes = notes
            if syllabus_id:
                coverage.syllabus = get_object_or_404(Syllabus, id=syllabus_id)
            else:
                coverage.syllabus = None
            coverage.save()
            
            return JsonResponse({'status': 'success', 'message': 'Exam schedule and coverage saved successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def delete_exam_schedule(request, exam_id):
    if request.session.get('user_type') not in ['admin', 'teacher']:
        return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)

    if request.method == 'POST':
        try:
            exam = get_object_or_404(ExamSchedule, id=exam_id)
            exam.delete()
            return JsonResponse({'status': 'success', 'message': 'Exam schedule deleted successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

class ExamScheduleViewSet(viewsets.ModelViewSet):
    queryset = ExamSchedule.objects.all()
    serializer_class = ExamScheduleSerializer
