from django.db import models
from StudentRecords.models import Student

class Subject(models.Model):
    GRADE_CHOICES = [
        ('Grade 1', 'Grade 1'),
        ('Grade 2', 'Grade 2'),
        ('Grade 3', 'Grade 3'),
        ('Grade 4', 'Grade 4'),
        ('Grade 5', 'Grade 5'),
        ('Grade 6', 'Grade 6'),
    ]

    name = models.CharField(max_length=200)
    grade_level = models.CharField(max_length=20, choices=GRADE_CHOICES)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('name', 'grade_level')
        ordering = ['grade_level', 'order', 'name']

    def __str__(self):
        return f"{self.name} ({self.grade_level})"


class Grade(models.Model):
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name="grades"
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE, 
        related_name="student_scores"
    )
    score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    term = models.CharField(max_length=50)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ('student', 'subject', 'term')

    def __str__(self):
        return f"{self.student.last_name} | {self.subject.name} | {self.term} : {self.score}"