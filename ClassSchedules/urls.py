from rest_framework import routers
from .views import ClassScheduleViewSet, save_class_schedule, delete_class_schedule
from django.urls import include, path

router = routers.DefaultRouter()
router.register("api", ClassScheduleViewSet, basename="classschedules")

urlpatterns = [
    path("", include(router.urls)),
    path("save/", save_class_schedule, name="save_class_schedule"),
    path("delete/<int:schedule_id>/", delete_class_schedule, name="delete_class_schedule"),
]
