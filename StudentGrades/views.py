import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from rest_framework import viewsets
from .models import Grade, Subject
from .serializers import GradeSerializer
from StudentRecords.models import Student

def report_cards_view(request):
    if request.session.get('user_type') != 'student':
        return redirect('login')
        
    user_email = request.session.get('user_email')
    selected_student = Student.objects.filter(email=user_email).first()
    current_level = selected_student.grade_level if selected_student else "Grade 1"
    
    grades_list = []
    average = 0
    
    if selected_student:
        subjects = Subject.objects.filter(grade_level=current_level).order_by('order')
        for sub in subjects:
            raw_scores = Grade.objects.filter(student=selected_student, subject=sub)
            row = {'subject': sub, 'q1': '-', 'q2': '-', 'q3': '-', 'q4': '-', 'final_grade': '-'}
            for g in raw_scores:
                if '1st' in g.term: row['q1'] = g.score
                elif '2nd' in g.term: row['q2'] = g.score
                elif '3rd' in g.term: row['q3'] = g.score
                elif '4th' in g.term: row['q4'] = g.score
            
            numeric_qs = [float(q) for q in [row['q1'], row['q2'], row['q3'], row['q4']] if q != '-']
            if numeric_qs:
                row['final_grade'] = sum(numeric_qs) / len(numeric_qs)
            grades_list.append(row)

        valid_finals = [g['final_grade'] for g in grades_list if g['final_grade'] != '-']
        if valid_finals:
            average = sum(valid_finals) / len(valid_finals)

    return render(request, 'report_cards.html', {
        'selected_student': selected_student,
        'grades': grades_list,
        'average': round(average, 2)
    })

def edit_report_cards_view(request):
    allowed_roles = ['staff', 'admin', 'coordinator']
    if request.session.get('user_type') not in allowed_roles:
        return redirect('login')
        
    students = Student.objects.all()
    selected_student_id = request.GET.get('student_id')
    selected_student = Student.objects.filter(id=selected_student_id).first() if selected_student_id else students.first()

    current_view_level = request.GET.get('view_grade_level')
    if not current_view_level and selected_student:
        current_view_level = selected_student.grade_level or "Grade 1"

    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            grades_data = data.get('grades', [])
            
            for item in grades_data:
                subject_obj = Subject.objects.get(id=item['subject_id'])
                quarters = {'1st Quarter': item['q1'], '2nd Quarter': item['q2'], '3rd Quarter': item['q3'], '4th Quarter': item['q4']}
                
                for term, score in quarters.items():
                    if score != '' and score != '-':
                        Grade.objects.update_or_create(
                            student=selected_student,
                            subject=subject_obj,
                            term=term,
                            defaults={'score': float(score)}
                        )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    grades_list = []
    average = 0
    if selected_student:
        subjects = Subject.objects.filter(grade_level=current_view_level).order_by('order')
        for sub in subjects:
            raw_scores = Grade.objects.filter(student=selected_student, subject=sub)
            row = {'subject': sub, 'q1': '-', 'q2': '-', 'q3': '-', 'q4': '-', 'final_grade': '-'}
            for g in raw_scores:
                if '1st' in g.term: row['q1'] = g.score
                elif '2nd' in g.term: row['q2'] = g.score
                elif '3rd' in g.term: row['q3'] = g.score
                elif '4th' in g.term: row['q4'] = g.score

            numeric_qs = [float(q) for q in [row['q1'], row['q2'], row['q3'], row['q4']] if q != '-']
            if numeric_qs:
                row['final_grade'] = sum(numeric_qs) / len(numeric_qs)
            grades_list.append(row)

        valid_finals = [g['final_grade'] for g in grades_list if g['final_grade'] != '-']
        if valid_finals:
            average = sum(valid_finals) / len(valid_finals)
       
    return render(request, 'edit_report_cards.html', {
        'students': students,
        'selected_student': selected_student,
        'current_view_level': current_view_level,
        'grades': grades_list,
        'average': round(average, 2)
    })

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer