from rest_framework import routers
from .views import ExamScheduleViewSet, exam_schedule_view
from django.urls import include, path

router = routers.DefaultRouter()
router.register("api", ExamScheduleViewSet, basename="exams-api")

urlpatterns = [
    path("", exam_schedule_view, name="exam-schedule"),
    path("api/", include(router.urls))
]
