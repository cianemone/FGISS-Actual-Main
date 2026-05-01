from rest_framework import routers
from .views import ParentViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register("", ParentViewSet, basename="parents")

urlpatterns = [path("", include(router.urls))]
