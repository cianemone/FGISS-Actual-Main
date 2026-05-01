from rest_framework import routers
from .views import UserViewSet, RoleViewSet, UserProfileViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register("accounts", UserViewSet, basename="accounts")
router.register("roles", RoleViewSet, basename="roles")
router.register("profiles", UserProfileViewSet, basename="profiles")

urlpatterns = [path("", include(router.urls))]
