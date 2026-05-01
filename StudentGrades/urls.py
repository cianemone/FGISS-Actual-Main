from django.urls import include, path
from rest_framework import routers
from .views import GradeViewSet, report_cards_view, edit_report_cards_view 

router = routers.DefaultRouter()
router.register("", GradeViewSet, basename="grades")

urlpatterns = [
    path("report-cards/", report_cards_view, name="report-cards"),
    path("edit-report-cards/", edit_report_cards_view, name="edit-report-cards"), 
    path("", include(router.urls)),
]