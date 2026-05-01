from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    def validate_student_number(self, value):
        instance = self.instance
        if instance and instance.student_number == value:
            return value
        if Student.objects.filter(student_number=value).exists():
            raise serializers.ValidationError("Student number already exists")
        return value
    
    def validate_email(self, value):
        if value:
            instance = self.instance
            if instance and instance.email == value:
                return value
            if Student.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email already exists")
        return value