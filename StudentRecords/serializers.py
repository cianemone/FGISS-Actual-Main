from rest_framework import serializers
from .models import Student
import re

class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    def validate_student_number(self, value):
        if not re.match(r'^stu\d{4}$', value):
            raise serializers.ValidationError("Student number must be in the format stuXXXX (e.g., stu0001)")
            
        instance = self.instance
        if instance and instance.student_number == value:
            return value
        if Student.objects.filter(student_number=value).exists():
            raise serializers.ValidationError("Student number already exists")
        return value
    
    def validate_email(self, value):
        if value:
            if not value.endswith('@fgiss.edu'):
                raise serializers.ValidationError("Email must end with @fgiss.edu")
                
            instance = self.instance
            if instance and instance.email == value:
                return value
            if Student.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email already exists")
        return value

    def validate(self, data):
        # Unique constraint for first_name and last_name
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        if first_name and last_name:
            instance = self.instance
            qs = Student.objects.filter(first_name=first_name, last_name=last_name)
            if instance:
                qs = qs.exclude(id=instance.id)
            if qs.exists():
                raise serializers.ValidationError({
                    "first_name": "A student with this first and last name already exists.",
                    "last_name": "A student with this first and last name already exists."
                })
        return data