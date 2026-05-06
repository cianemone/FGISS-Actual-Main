from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_syllabus_view, name='course_syllabus'),
    path('create/', views.syllabus_create, name='syllabus_create'),
    path('update/<int:pk>/', views.syllabus_update, name='syllabus_update'),
    path('delete/<int:pk>/', views.syllabus_delete, name='syllabus_delete'),
]
