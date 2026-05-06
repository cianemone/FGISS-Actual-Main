from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Syllabus
from StudentRecords.models import Student

# Common subjects for Grades 1-6
SUBJECTS = [
    "Mathematics", "English", "Science", "Filipino", 
    "Araling Panlipunan", "MAPEH (Music)", "MAPEH (Arts)", 
    "MAPEH (Physical Education)", "MAPEH (Health)", 
    "ESP (Edukasyon sa Pagpapakatao)", "Computer", 
    "HELE (Home Economics and Livelihood Education)"
]

def course_syllabus_view(request):
    user_type = request.session.get('user_type')
    user_email = request.session.get('user_email')
    
    if not user_type:
        return redirect('login')
    
    student = None
    if user_type == 'student':
        student = Student.objects.filter(email=user_email).first()
        if not student:
            # Fallback if student record not found
            syllabi = Syllabus.objects.none()
        else:
            # Students only see syllabi for their grade level
            syllabi = Syllabus.objects.filter(grade_level=student.grade_level)
    elif user_type in ['admin', 'staff', 'teacher']:
        # Admin/Staff/Teacher see all
        syllabi = Syllabus.objects.all()
    else:
        # Coordinators and others have no access
        return redirect('login')

    # Filtering logic
    search_query = request.GET.get('search', '')
    if search_query:
        syllabi = syllabi.filter(title__icontains=search_query)

    return render(request, 'course_syllabus.html', {
        'syllabi': syllabi,
        'user_email': user_email,
        'student': student,
        'subjects': SUBJECTS,
        'search_query': search_query
    })

def syllabus_create(request):
    if request.session.get('user_type') not in ['admin', 'staff', 'teacher']:
        return redirect('course_syllabus')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        grade_level = request.POST.get('grade_level')
        description = request.POST.get('description')
        topics = request.POST.get('topics')
        
        Syllabus.objects.create(
            title=title,
            grade_level=grade_level,
            description=description,
            topics=topics
        )
        messages.success(request, 'Syllabus created successfully!')
        return redirect('course_syllabus')
        
    return render(request, 'syllabus_form.html', {
        'subjects': SUBJECTS,
        'grade_choices': Syllabus.GRADE_CHOICES
    })

def syllabus_update(request, pk):
    if request.session.get('user_type') not in ['admin', 'staff', 'teacher']:
        return redirect('course_syllabus')
    
    syllabus = get_object_or_404(Syllabus, pk=pk)
    
    if request.method == 'POST':
        syllabus.title = request.POST.get('title')
        syllabus.grade_level = request.POST.get('grade_level')
        syllabus.description = request.POST.get('description')
        syllabus.topics = request.POST.get('topics')
        syllabus.save()
        messages.success(request, 'Syllabus updated successfully!')
        return redirect('course_syllabus')
        
    return render(request, 'syllabus_form.html', {
        'syllabus': syllabus,
        'subjects': SUBJECTS,
        'grade_choices': Syllabus.GRADE_CHOICES
    })

def syllabus_delete(request, pk):
    if request.session.get('user_type') not in ['admin', 'staff', 'teacher']:
        return redirect('course_syllabus')
    
    syllabus = get_object_or_404(Syllabus, pk=pk)
    if request.method == 'POST':
        syllabus.delete()
        messages.success(request, 'Syllabus deleted successfully!')
    return redirect('course_syllabus')
