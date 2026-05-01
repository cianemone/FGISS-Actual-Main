from rest_framework import routers
from .views import StudentViewSet
from django.urls import path, include
from . import views

# API Router
router = routers.DefaultRouter()
router.register(r'', StudentViewSet, basename='students')

urlpatterns = [
    # API endpoints (will be at /api/students/)
    path('', include(router.urls)),
    
    # Web interface endpoints
    path('web/records/', views.student_list_view, name='student_list'),
    path('web/records/add/', views.student_form_view, name='student_add'),
    path('web/records/edit/', views.student_form_view, name='student_edit'),
    path('web/records/<str:student_number>/', views.student_detail_view, name='student_detail'),
    path('web/records/<str:student_number>/delete/', views.student_delete_view, name='student_delete'),
    
    # Student self-service
    path('self/edit/', views.student_self_edit_view, name='student_self_edit'),
]