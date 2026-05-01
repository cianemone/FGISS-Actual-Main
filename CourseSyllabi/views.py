from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import Syllabus
from .serializers import SyllabusSerializer

def course_syllabus_view(request):
    # Check if user has permission (admin, staff, or student)
    allowed_roles = ['admin', 'staff', 'student']
    if request.session.get('user_type') not in allowed_roles:
        return redirect('login')
    
    syllabi = Syllabus.objects.all()
    
    return render(request, 'course_syllabus.html', {
        'syllabi': syllabi,
        'user_email': request.session.get('user_email')
    })

class SyllabusViewSet(viewsets.ModelViewSet):
    queryset = Syllabus.objects.all()
    serializer_class = SyllabusSerializer
