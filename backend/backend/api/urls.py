from django.urls import path
from .views import ResumeUploadView, SkillMatchView

urlpatterns = [
    path('upload_resume/', ResumeUploadView.as_view(), name='upload_resume'),
    path('match_skill/', SkillMatchView.as_view(), name='match_skill'),
]
