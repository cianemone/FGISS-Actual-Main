from rest_framework import serializers
from .models import ExamSchedule

class ExamScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSchedule
        fields = "__all__"
