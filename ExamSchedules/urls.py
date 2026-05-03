from rest_framework import routers
from .views import ExamScheduleViewSet, exam_schedule_view, edit_exam_schedule_view, save_exam_schedule, delete_exam_schedule
from django.urls import include, path

router = routers.DefaultRouter()
router.register("api", ExamScheduleViewSet, basename="exams-api")

urlpatterns = [
    path("", exam_schedule_view, name="exam-schedule"),
    path("edit/", edit_exam_schedule_view, name="edit-exam-schedule"),
    path("save/", save_exam_schedule, name="save_exam_schedule"),
    path("delete/<int:exam_id>/", delete_exam_schedule, name="delete_exam_schedule"),
    path("api-router/", include(router.urls))
]
