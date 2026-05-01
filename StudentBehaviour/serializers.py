from rest_framework import serializers
from .models import BehaviourIncident, InterventionPlan

class BehaviourIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BehaviourIncident
        fields = "__all__"

class InterventionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterventionPlan
        fields = "__all__"
