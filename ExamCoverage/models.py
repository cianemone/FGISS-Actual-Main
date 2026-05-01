from django.db import models
from ExamSchedules.models import ExamSchedule
from CourseSyllabi.models import Syllabus

class ExamCoverage(models.Model):
    exam = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name="coverages")
    syllabus = models.ForeignKey(Syllabus, on_delete=models.SET_NULL, null=True, blank=True)
    topics_covered = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Coverage for {self.exam}"
