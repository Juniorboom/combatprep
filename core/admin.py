from django.contrib import admin
from .models import User, SoldierProfile, Assessment, ReadinessScore


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'get_full_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')


@admin.register(SoldierProfile)
class SoldierProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rank', 'service_number', 'branch', 'unit')
    list_filter = ('rank', 'branch')
    search_fields = ('service_number', 'user__username')


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('soldier', 'assessed_by', 'assessment_type', 'result', 'date')
    list_filter = ('assessment_type', 'result')


@admin.register(ReadinessScore)
class ReadinessScoreAdmin(admin.ModelAdmin):
    list_display = ('soldier', 'scored_by', 'physical_score', 'mental_score', 'equipment_score', 'overall_score', 'date')
    list_filter = ('date',)
