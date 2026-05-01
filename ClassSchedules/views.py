from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import ClassSchedule
from .serializers import ClassScheduleSerializer

def class_schedule_view(request):
    # Check if user has permission (admin or staff)
    allowed_roles = ['admin', 'staff']
    if request.session.get('user_type') not in allowed_roles:
        return redirect('login')
    
    schedules = ClassSchedule.objects.all().order_by('day_of_week', 'start_time')
    
    return render(request, 'class_schedule.html', {
        'schedules': schedules,
        'user_email': request.session.get('user_email')
    })

class ClassScheduleViewSet(viewsets.ModelViewSet):
    queryset = ClassSchedule.objects.all()
    serializer_class = ClassScheduleSerializer
