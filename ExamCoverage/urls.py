from rest_framework import routers
from .views import ExamCoverageViewSet
from django.urls import include, path

router = routers.DefaultRouter()
router.register("", ExamCoverageViewSet, basename="examcoverage")

urlpatterns = [path("", include(router.urls))]
