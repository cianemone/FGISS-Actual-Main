from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from ParentRecords.models import Parent

def validate_fgiss_email(value):
    if not value.endswith('@fgiss.edu'):
        raise ValidationError('Email must end with @fgiss.edu')

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    student_number = models.CharField(
        max_length=50, 
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^stu\d{4}$',
                message='Student number must be in the format stuXXXX (e.g., stu0001)',
                code='invalid_student_number'
            )
        ]
    )
    email = models.EmailField(
        unique=True, 
        null=True, 
        blank=True,
        validators=[validate_fgiss_email]
    )
    dob = models.DateField(null=True, blank=True)
    parent = models.ForeignKey(Parent, on_delete=models.SET_NULL, null=True, blank=True, related_name="children")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    #Emenrgency Number
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True, null=True)
    
    #Section and Class
    section = models.CharField(max_length=50, blank=True, null=True)
    grade_level = models.CharField(max_length=20, blank=True, null=True)
    # Enrollment tracking
    date_of_enrollment = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Timestamps 
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['first_name', 'last_name'], name='unique_student_name')
        ]

    def __str__(self):
        return f"{self.student_number} - {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"