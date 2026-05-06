from django.db import models

class Syllabus(models.Model):
    GRADE_CHOICES = [
        ('Grade 1', 'Grade 1'),
        ('Grade 2', 'Grade 2'),
        ('Grade 3', 'Grade 3'),
        ('Grade 4', 'Grade 4'),
        ('Grade 5', 'Grade 5'),
        ('Grade 6', 'Grade 6'),
    ]

    title = models.CharField(max_length=200)
    grade_level = models.CharField(max_length=20, choices=GRADE_CHOICES, default='Grade 1')
    description = models.TextField(blank=True)
    topics = models.TextField(blank=True)  # newline separated or JSON for demo

    def __str__(self):
        return f"{self.grade_level} - {self.title}"
