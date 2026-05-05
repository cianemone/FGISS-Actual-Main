from django.test import TestCase, Client
from django.urls import reverse
from .models import ExamSchedule
from ClassSchedules.models import ClassSchedule
from StudentGrades.models import Subject
import json
from datetime import time, date

class ScheduleConflictTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.subject = Subject.objects.create(name="Math", grade_level="Grade 1")
        
        # Create an existing ClassSchedule
        self.class_sched = ClassSchedule.objects.create(
            subject=self.subject,
            section="A",
            day_of_week="Monday",
            start_time=time(10, 0),
            end_time=time(11, 0),
            room="Room 101"
        )
        
        # Create an existing ExamSchedule
        self.exam_sched = ExamSchedule.objects.create(
            name="Midterm",
            date=date(2026, 5, 11),  # This is a Monday
            start_time=time(13, 0),
            end_time=time(14, 0),
            room="Room 101"
        )

    def test_exam_conflict_with_exam(self):
        # Try to add an exam that overlaps with the existing Midterm
        url = reverse('save_exam_schedule')
        data = {
            'name': 'Overlapping Exam',
            'date': '2026-05-11',
            'start_time': '13:30',
            'end_time': '14:30',
            'room': 'Room 101'
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        result = response.json()
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('Conflict', result['message'])
        self.assertIn('Midterm', result['message'])

    def test_exam_conflict_with_class(self):
        # Try to add an exam that overlaps with the existing Math class
        url = reverse('save_exam_schedule')
        data = {
            'name': 'Exam during Class',
            'date': '2026-05-11', # Monday
            'start_time': '10:30',
            'end_time': '11:30',
            'room': 'Room 101'
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        result = response.json()
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('Conflict', result['message'])
        self.assertIn('Math', result['message'])

    def test_class_conflict_with_class(self):
        # Try to add a class that overlaps with the existing Math class
        # Note: ClassSchedule save URL is /api/schedules/save/ in ClassSchedules/urls.py
        # But it's included as path("api/schedules/", include("ClassSchedules.urls")) in FGISS/urls.py
        # reverse('save_class_schedule') should work if name is unique
        url = reverse('save_class_schedule')
        data = {
            'subject_id': self.subject.id,
            'section': 'B',
            'teacher_name': 'Prof. X',
            'day_of_week': 'Monday',
            'start_time': '10:30',
            'end_time': '11:30',
            'room': 'Room 101'
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        result = response.json()
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('Conflict', result['message'])
        self.assertIn('Math', result['message'])

    def test_class_conflict_with_exam(self):
        # Try to add a class that overlaps with the existing Midterm exam
        url = reverse('save_class_schedule')
        data = {
            'subject_id': self.subject.id,
            'section': 'C',
            'teacher_name': 'Prof. Y',
            'day_of_week': 'Monday',
            'start_time': '13:30',
            'end_time': '14:30',
            'room': 'Room 101'
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        result = response.json()
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('Conflict', result['message'])
        self.assertIn('Midterm', result['message'])

    def test_update_exam_no_self_conflict(self):
        # Update existing exam, should NOT conflict with itself
        url = reverse('save_exam_schedule')
        data = {
            'id': self.exam_sched.id,
            'name': 'Midterm Updated',
            'date': '2026-05-11',
            'start_time': '13:00',
            'end_time': '14:00',
            'room': 'Room 101'
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        result = response.json()
        
        self.assertEqual(result['status'], 'success')

    def test_update_class_no_self_conflict(self):
        # Update existing class, should NOT conflict with itself
        url = reverse('save_class_schedule')
        data = {
            'id': self.class_sched.id,
            'subject_id': self.subject.id,
            'section': 'A Updated',
            'teacher_name': 'Prof. Z',
            'day_of_week': 'Monday',
            'start_time': '10:00',
            'end_time': '11:00',
            'room': 'Room 101'
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        result = response.json()
        
        self.assertEqual(result['status'], 'success')
