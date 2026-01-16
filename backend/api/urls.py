from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import auth_views
from . import search_views
from . import resume_views
from . import message_views
from . import learning_views
from . import rating_views

router = DefaultRouter()
router.register(r'skills', views.SkillViewSet, basename='skills')
router.register(r'notifications', views.NotificationViewSet, basename='notifications')

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
    path('streaks/', views.LoginStreakView.as_view(), name='login_streaks'),
    path('debug/reload-model/', views.ModelReloadView.as_view(), name='reload_model'),
    
    # Learning session endpoints
    path('learning/join/', learning_views.join_learning, name='join_learning'),
    path('learning/requests/', learning_views.get_learning_requests, name='learning_requests'),
    path('learning/requests/<int:session_id>/accept/', learning_views.accept_learning_request, name='accept_learning_request'),
    path('learning/requests/<int:session_id>/reject/', learning_views.reject_learning_request, name='reject_learning_request'),
    path('learning/end/<int:session_id>/', learning_views.end_learning, name='end_learning'),
    path('learning/sessions/', learning_views.get_learning_sessions, name='learning_sessions'),
    path('learning/sessions/<int:session_id>/', learning_views.get_learning_session_detail, name='learning_session_detail'),
    path('learning/points/', learning_views.get_user_points, name='user_points'),
    path('learning/skills-learned/', learning_views.get_skills_learned, name='skills_learned'),
    path('learning/skills-learned/<str:username>/', learning_views.get_skills_learned, name='skills_learned_user'),
    path('learning/skills-taught/', learning_views.get_skills_taught, name='skills_taught'),
    path('learning/skills-taught/<str:username>/', learning_views.get_skills_taught, name='skills_taught_user'),
    path('learning/badges/', learning_views.get_user_badges, name='user_badges'),
    path('learning/badges/<str:username>/', learning_views.get_user_badges, name='user_badges_by_username'),
    
    # Rating endpoints
    path('learning/rate/<int:session_id>/', rating_views.submit_rating, name='submit_rating'),
    path('learning/ratings/<int:session_id>/', rating_views.get_session_ratings, name='session_ratings'),
    path('learning/ratings/user/', rating_views.get_user_ratings, name='user_ratings'),
    path('learning/ratings/user/<str:username>/', rating_views.get_user_ratings, name='user_ratings_by_username'),
    path('learning/can-rate/<int:session_id>/', rating_views.check_can_rate, name='check_can_rate'),
]