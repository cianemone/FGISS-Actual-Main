from django.db import models
from ClassSchedules.models import ClassSchedule

class ExamSchedule(models.Model):
    name = models.CharField(max_length=200)
    class_schedule = models.ForeignKey(ClassSchedule, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.name} on {self.date}"
