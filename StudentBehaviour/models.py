from django.db import models
from StudentRecords.models import Student

SEVERITY_CHOICES = (("low", "Low"), ("medium", "Medium"), ("high", "High"))

class BehaviourIncident(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="incidents")
    occurred_at = models.DateTimeField()
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="low")
    action_taken = models.TextField(blank=True)

    def __str__(self):
        return f"Incident for {self.student} on {self.occurred_at.date()}"

class InterventionPlan(models.Model):
    INTERVENTION_TYPES = (
        ("Academic Support", "Academic Support"),
        ("Behavioral Modification", "Behavioral Modification"),
        ("Social-Emotional Learning", "Social-Emotional Learning"),
        ("Attendance Contract", "Attendance Contract"),
    )
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="intervention_plan")
    intervention_type = models.CharField(max_length=50, choices=INTERVENTION_TYPES)
    start_date = models.DateField()
    review_date = models.DateField()
    primary_goal = models.TextField()

    def __str__(self):
        return f"Intervention Plan for {self.student}"
