from django.db import models
from StudentGrades.models import Subject

class ClassSchedule(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="schedules", null=True, blank=True)
    section = models.CharField(max_length=50, blank=True, null=True) # e.g., 7-Alpha
    teacher_name = models.CharField(max_length=100, blank=True, null=True)
    day_of_week = models.CharField(max_length=20)  # e.g., Monday
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)

    def __str__(self):
        subject_name = self.subject.name if self.subject else "No Subject"
        return f"{subject_name} | {self.day_of_week} {self.start_time}-{self.end_time}"
