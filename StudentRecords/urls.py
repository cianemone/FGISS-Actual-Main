from rest_framework import routers
from .views import StudentViewSet
from django.urls import path, include
from . import views

router = routers.DefaultRouter()
router.register(r'', StudentViewSet, basename='students')

urlpatterns = [
    path('', include(router.urls)),
    
    path('web/records/', views.student_list_view, name='student_list'),
    path('web/records/add/', views.student_form_view, name='student_add'),
    path('web/records/edit/', views.student_form_view, name='student_edit'),
    path('web/records/<str:student_number>/', views.student_detail_view, name='student_detail'),
    path('web/records/<str:student_number>/delete/', views.student_delete_view, name='student_delete'),
    
    path('web/incidents/', views.incident_report_view, name='incident_report'),
    path('save-incident-report/', views.incident_report_view, name='save_incident_report'),
    
    path('self/edit/', views.student_self_edit_view, name='student_self_edit'),
]