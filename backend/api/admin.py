from django.contrib import admin
from .models import (
    UserProfile, Skill, Resume, SkillMatch,
    LearningSession, UserPoints, PointTransaction, SkillRating, PointConfiguration, Badge
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username', 'bio')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'proficiency_level', 'created_at')
    list_filter = ('proficiency_level', 'created_at')
    search_fields = ('name', 'user__username', 'description')

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'processed', 'created_at')
    list_filter = ('processed', 'created_at')
    search_fields = ('user__username',)

@admin.register(SkillMatch)
class SkillMatchAdmin(admin.ModelAdmin):
    list_display = ('seeker', 'provider', 'desired_skill', 'similarity_score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('seeker__username', 'provider__username', 'desired_skill')


@admin.register(PointConfiguration)
class PointConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'created_at', 'updated_at')
    search_fields = ('name', 'description')


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'total_earned', 'total_spent', 'updated_at')
    search_fields = ('user__username',)
    list_filter = ('updated_at',)


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'balance_after', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__username', 'description')


@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ('learner', 'teacher', 'skill_name', 'status', 'total_days', 'start_date', 'end_date')
    list_filter = ('status', 'created_at')
    search_fields = ('learner__username', 'teacher__username', 'skill_name')


@admin.register(SkillRating)
class SkillRatingAdmin(admin.ModelAdmin):
    list_display = ('rater', 'rated_user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('rater__username', 'rated_user__username', 'feedback')


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge_type', 'earned_at')
    list_filter = ('badge_type', 'earned_at')
    search_fields = ('user__username',)
