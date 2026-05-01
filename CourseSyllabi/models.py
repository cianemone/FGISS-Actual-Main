from django.db import models

class Syllabus(models.Model):
    course_code = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    topics = models.TextField(blank=True)  # newline separated or JSON for demo

    def __str__(self):
        return f"{self.course_code} - {self.title}"
