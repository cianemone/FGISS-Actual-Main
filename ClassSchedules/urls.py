from rest_framework import routers
from .views import ClassScheduleViewSet
from django.urls import include, path

router = routers.DefaultRouter()
router.register("", ClassScheduleViewSet, basename="classschedules")

urlpatterns = [path("", include(router.urls))]
