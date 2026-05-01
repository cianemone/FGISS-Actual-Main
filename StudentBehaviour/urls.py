from rest_framework import routers
from .views import BehaviourIncidentViewSet
from django.urls import include, path

router = routers.DefaultRouter()
router.register("", BehaviourIncidentViewSet, basename="incidents")

urlpatterns = [path("", include(router.urls))]
