from rest_framework import viewsets
from .models import Parent
from .serializers import ParentSerializer

class ParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.all().order_by("last_name")
    serializer_class = ParentSerializer
