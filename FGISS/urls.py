from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import routers
from Otherstuff import views as other_views
from StudentGrades.views import report_cards_view, edit_report_cards_view
from UsersANDuserRoles.views import login_check_view, logout_view, admin_dashboard_view, user_roles_view, create_user_view, delete_user_view
from StudentBehaviour.views import intervention_plan_view, save_intervention_plan, delete_intervention_plan
from CourseSyllabi.views import course_syllabus_view
from ExamSchedules.views import exam_schedule_view
from ClassSchedules.views import class_schedule_view
from UsersANDuserRoles.views import student_dashboard_view
from StudentRecords import views as student_views

urlpatterns = [
    path("", TemplateView.as_view(template_name="login.html"), name="login"),
    path("login-check/", login_check_view, name="login-check"),
    path("logout/", logout_view, name="logout"),
    path("admin-dashboard/", admin_dashboard_view, name="admin-dashboard"),
    path("user-roles/", user_roles_view, name="user-roles"),
    path("create-user/", create_user_view, name="create-user"),
    path("delete-user/<int:user_id>/", delete_user_view, name="delete-user"),
    path("admin/", admin.site.urls),
    path("report-cards/", report_cards_view, name="top-report-cards"),
    path("edit-report-cards/", edit_report_cards_view, name="edit-report-cards"),
    path("intervention-plan/", intervention_plan_view, name="intervention-plan"),
    path("save-intervention-plan/", save_intervention_plan, name="save-intervention-plan"),
    path("delete-intervention-plan/<int:student_id>/", delete_intervention_plan, name="delete-intervention-plan"),
    path("course-syllabus/", course_syllabus_view, name="course-syllabus"),
    path("exam-schedule/", include("ExamSchedules.urls")),
    path("class-schedule/", class_schedule_view, name="class-schedule"),
    path("api/health/", other_views.HealthCheck.as_view(), name="health"),
    path("api/users/", include("UsersANDuserRoles.urls")),
    path("api/parents/", include("ParentRecords.urls")),
    path("api/students/", include("StudentRecords.urls")),  # MAKE SURE THIS LINE EXISTS
    path("students/", include("StudentRecords.urls")),  # FOR WEB INTERFACE
    path("api/grades/", include("StudentGrades.urls")),
    path("student/dashboard/", student_dashboard_view, name="student_dashboard"),
    path('incident-report/', student_views.incident_report_view, name='incident_report'),
    path('save-incident-report/', student_views.incident_report_view, name='save_incident_report'),
    path('delete-incident-report/<int:report_id>/', student_views.delete_incident_report, name='delete_incident_report'),

    path("api/behaviour/", include("StudentBehaviour.urls")),
    path("api/schedules/", include("ClassSchedules.urls")),
    path("api/exams/", include("ExamSchedules.urls")),
    path("api/examcoverage/", include("ExamCoverage.urls")),
    path("api/syllabi/", include("CourseSyllabi.urls")),
]