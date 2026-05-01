from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import ExamSchedule
from .serializers import ExamScheduleSerializer

def exam_schedule_view(request):
    # Check if user has permission (admin, staff, or student)
    allowed_roles = ['admin', 'staff', 'student']
    if request.session.get('user_type') not in allowed_roles:
        return redirect('login')
    
    exams = ExamSchedule.objects.all().order_by('date', 'start_time')
    
    return render(request, 'exam_schedule.html', {
        'exams': exams,
        'user_email': request.session.get('user_email')
    })

class ExamScheduleViewSet(viewsets.ModelViewSet):
    queryset = ExamSchedule.objects.all()
    serializer_class = ExamScheduleSerializer
