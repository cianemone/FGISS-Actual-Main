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

    student = None
    if request.session.get('user_type') == 'student':
        from StudentRecords.models import Student
        student = Student.objects.filter(email=request.session.get('user_email')).first()

    return render(request, 'course_syllabus.html', {
        'syllabi': syllabi,
        'user_email': request.session.get('user_email'),
        'student': student
    })
class SyllabusViewSet(viewsets.ModelViewSet):
    queryset = Syllabus.objects.all()
    serializer_class = SyllabusSerializer
