from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from .models import BehaviourIncident, InterventionPlan
from .serializers import BehaviourIncidentSerializer
from StudentRecords.models import Student

def intervention_plan_view(request):
    # Check if user has permission (guidance, admin, or coordinator)
    allowed_roles = ['guidance', 'admin', 'coordinator', 'staff', 'teacher']
    if request.session.get('user_type') not in allowed_roles:
        return redirect('login')
        
    students = Student.objects.all().order_by('last_name', 'first_name')
    selected_student_id = request.GET.get('student_id')
    
    selected_student = None
    if selected_student_id:
        selected_student = Student.objects.filter(id=selected_student_id).first()
    else:
        # Default to first student if none selected, but let's see if we want that
        selected_student = students.first()
        
    intervention_plan = None
    has_plan = False
    if selected_student:
        intervention_plan = InterventionPlan.objects.filter(student=selected_student).first()
        has_plan = intervention_plan is not None
        
    return render(request, 'intervention_plan.html', {
        'students': students,
        'selected_student': selected_student,
        'intervention_plan': intervention_plan,
        'has_plan': has_plan,
        'intervention_types': InterventionPlan.INTERVENTION_TYPES
    })

def save_intervention_plan(request):
    allowed_roles = ['guidance', 'admin', 'coordinator', 'staff', 'teacher']
    if request.session.get('user_type') not in allowed_roles:
        return redirect('login')

    if request.method == "POST":
        student_id = request.POST.get('student_id')
        student = get_object_or_404(Student, id=student_id)
        
        intervention_type = request.POST.get('intervention_type')
        start_date = request.POST.get('start_date')
        review_date = request.POST.get('review_date')
        primary_goal = request.POST.get('primary_goal')
        
        # Validation: check if dates are provided
        if not start_date or not review_date:
             # Basic error handling, in a real app use Forms
             return redirect(f'/intervention-plan/?student_id={student_id}&error=missing_dates')

        plan, created = InterventionPlan.objects.update_or_create(
            student=student,
            defaults={
                'intervention_type': intervention_type,
                'start_date': start_date,
                'review_date': review_date,
                'primary_goal': primary_goal,
            }
        )
        return redirect(f'/intervention-plan/?student_id={student_id}')
    return redirect('intervention-plan')

def delete_intervention_plan(request, student_id):
    allowed_roles = ['guidance', 'admin', 'coordinator', 'staff', 'teacher']
    if request.session.get('user_type') not in allowed_roles:
        return redirect('login')

    student = get_object_or_404(Student, id=student_id)
    InterventionPlan.objects.filter(student=student).delete()
    return redirect(f'/intervention-plan/?student_id={student_id}')

class BehaviourIncidentViewSet(viewsets.ModelViewSet):
    queryset = BehaviourIncident.objects.all()
    serializer_class = BehaviourIncidentSerializer
    filterset_fields = ["student", "severity"]
