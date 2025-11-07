from django.contrib import admin
from .models import UserProfile, Skill, Resume, SkillMatch

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