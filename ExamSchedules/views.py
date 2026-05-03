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

def exam_schedule_view(request):
    """Student view-only exam schedule"""
    user_type = request.session.get('user_type')
    if user_type != 'student':
        return redirect('login')
    
    # Optional: Filter by student's grade/section if we want consistency with Class Schedule
    # For now, just show all exams or generic list as requested
    exams = ExamSchedule.objects.all().order_by('date', 'start_time')
    
    return render(request, 'exam_schedule.html', {
        'exams': exams,
        'user_email': request.session.get('user_email')
    })

def edit_exam_schedule_view(request):
    """Admin/Teacher view with CRUD capabilities"""
    user_type = request.session.get('user_type')
    allowed_roles = ['admin', 'staff', 'teacher']
    
    if user_type not in allowed_roles:
        return redirect('login')
    
    exams = ExamSchedule.objects.all().order_by('date', 'start_time')
    class_schedules = ClassSchedule.objects.all().order_by('subject__grade_level', 'section', 'subject__name')
    syllabi = Syllabus.objects.all().order_by('course_code')
    
    return render(request, 'edit_exam_schedule.html', {
        'exams': exams,
        'class_schedules': class_schedules,
        'syllabi': syllabi,
        'user_email': request.session.get('user_email')
    })

@csrf_exempt
def save_exam_schedule(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            exam_id = data.get('id')
            
            if exam_id:
                exam = get_object_or_404(ExamSchedule, id=exam_id)
            else:
                exam = ExamSchedule()
            
            exam.name = data.get('name')
            class_sched_id = data.get('class_schedule_id')
            if class_sched_id:
                exam.class_schedule = get_object_or_404(ClassSchedule, id=class_sched_id)
            
            exam.date = data.get('date')
            exam.start_time = data.get('start_time')
            exam.end_time = data.get('end_time')
            exam.room = data.get('room')
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
