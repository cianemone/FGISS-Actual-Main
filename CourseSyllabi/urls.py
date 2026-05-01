from rest_framework import routers
from .views import SyllabusViewSet, course_syllabus_view
from django.urls import include, path

router = routers.DefaultRouter()
router.register("api", SyllabusViewSet, basename="syllabi-api")

urlpatterns = [
    path("", course_syllabus_view, name="course-syllabus"),
    path("api/", include(router.urls))
]
