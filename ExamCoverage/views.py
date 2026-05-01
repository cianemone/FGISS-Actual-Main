from rest_framework import viewsets
from .models import ExamCoverage
from .serializers import ExamCoverageSerializer

class ExamCoverageViewSet(viewsets.ModelViewSet):
    queryset = ExamCoverage.objects.all()
    serializer_class = ExamCoverageSerializer
