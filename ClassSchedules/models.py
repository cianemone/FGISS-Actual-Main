from django.db import models
from django.contrib.auth.models import User

class ClassSchedule(models.Model):
    class_name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    day_of_week = models.CharField(max_length=20)  # e.g., Monday
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.class_name} | {self.day_of_week} {self.start_time}-{self.end_time}"
