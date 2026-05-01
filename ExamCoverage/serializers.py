from rest_framework import serializers
from .models import ExamCoverage

class ExamCoverageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamCoverage
        fields = "__all__"
