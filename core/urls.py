from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard router
    path('dashboard/', views.dashboard_router, name='dashboard'),

    # Admin
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/toggle-user/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),

    # Officer
    path('dashboard/officer/', views.officer_dashboard, name='officer_dashboard'),
    path('officer/assessment/new/', views.create_assessment, name='create_assessment'),
    path('officer/score/new/', views.record_score, name='record_score'),
    path('officer/assessments/', views.assessment_list, name='assessment_list'),
    path('officer/scores/', views.score_list, name='score_list'),

    # Soldier
    path('dashboard/soldier/', views.soldier_dashboard, name='soldier_dashboard'),
    path('soldier/profile/', views.edit_profile, name='edit_profile'),
    path('soldier/scores/', views.score_history, name='score_history'),
]
