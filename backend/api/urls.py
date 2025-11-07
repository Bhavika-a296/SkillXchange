from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import auth_views
from . import search_views
from . import resume_views
from . import message_views

router = DefaultRouter()
router.register(r'skills', views.SkillViewSet, basename='skills')

urlpatterns = [
    path('', include(router.urls)),
    # Custom profile endpoints to handle PATCH on list
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/<int:pk>/', views.UserProfileDetailView.as_view(), name='profile-detail'),
    path('auth/register/', auth_views.register_user, name='register'),
    path('auth/login/', auth_views.login_user, name='login'),
    path('auth/check-username/<str:username>/', auth_views.check_username, name='check_username'),
    path('upload_resume/', resume_views.ResumeUploadView.as_view(), name='upload_resume'),
    path('resume/current/', resume_views.ResumeUploadView.as_view(), name='current_resume'),
    path('match_skills/', views.SkillMatchView.as_view(), name='match_skills'),
    path('users/search/', search_views.search_users, name='search_users'),
    path('users/profile/<str:username>/', search_views.get_profile_by_username, name='get_profile_by_username'),
    path('connections/request/<int:user_id>/', views.ConnectionRequestView.as_view(), name='connection_request'),
    path('connections/', views.ConnectionsListView.as_view(), name='connections_list'),
    path('connections/<int:connection_id>/accept/', views.ConnectionAcceptView.as_view(), name='connection_accept'),
    path('connections/<int:connection_id>/reject/', views.ConnectionRejectView.as_view(), name='connection_reject'),
    path('messages/', message_views.MessageView.as_view(), name='messages'),
    path('conversations/', message_views.ConversationsListView.as_view(), name='conversations'),
    path('realtime/token/', message_views.AblyTokenView.as_view(), name='ably_token'),
]