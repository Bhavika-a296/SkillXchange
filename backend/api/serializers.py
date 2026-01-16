from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, Skill, Resume, SkillMatch, Connection, Message, Notification,
    LearningSession, UserPoints, PointTransaction, SkillRating, PointConfiguration, Badge
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('id', 'name', 'description', 'proficiency_level', 'created_at')
        read_only_fields = ('user',)

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True, source='user.skills.all')
    
    class Meta:
        model = UserProfile
        fields = ('user', 'bio', 'skills', 'created_at', 'updated_at')

class ResumeSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    filename = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = ('id', 'file', 'file_url', 'filename', 'processed', 'created_at', 'skills')
        read_only_fields = ('user', 'processed', 'file_url', 'filename', 'skills')

    def get_file_url(self, obj):
        return obj.file.url if obj.file else None

    def get_filename(self, obj):
        return obj.file.name.split('/')[-1] if obj.file else None

    def get_skills(self, obj):
        # Get all skills associated with the resume's user
        skills = obj.user.skills.all()
        return SkillSerializer(skills, many=True).data

class SkillMatchSerializer(serializers.ModelSerializer):
    provider = UserSerializer(read_only=True)
    
    class Meta:
        model = SkillMatch
        fields = ('id', 'provider', 'desired_skill', 'similarity_score', 'created_at')
        read_only_fields = ('seeker', 'provider', 'similarity_score')


class ConnectionSerializer(serializers.ModelSerializer):
    requester = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Connection
        fields = ('id', 'requester', 'receiver', 'status', 'created_at')
        read_only_fields = ('requester', 'receiver', 'created_at')


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('id', 'sender', 'receiver', 'content', 'file', 'file_url', 'file_name', 'created_at', 'read')
        read_only_fields = ('sender', 'created_at', 'file_url', 'file_name')

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_file_name(self, obj):
        return obj.file.name.split('/')[-1] if obj.file else None


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    sender_username = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ('id', 'notification_type', 'title', 'message', 'sender', 'sender_username', 'link', 'read', 'created_at')
        read_only_fields = ('user', 'sender', 'created_at')

    def get_sender_username(self, obj):
        return obj.sender.username if obj.sender else None


class UserPointsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserPoints
        fields = ('id', 'user', 'username', 'balance', 'total_earned', 'total_spent', 'updated_at')
        read_only_fields = ('user', 'username', 'updated_at')


class PointTransactionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PointTransaction
        fields = ('id', 'user', 'username', 'transaction_type', 'amount', 'balance_after', 'description', 'created_at')
        read_only_fields = ('user', 'username', 'created_at')


class PointConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointConfiguration
        fields = ('id', 'name', 'value', 'description', 'created_at', 'updated_at')


class LearningSessionSerializer(serializers.ModelSerializer):
    learner = UserSerializer(read_only=True)
    teacher = UserSerializer(read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = LearningSession
        fields = (
            'id', 'learner', 'teacher', 'skill_name', 'status',
            'total_days', 'start_date', 'end_date',
            'points_deducted', 'points_awarded_learner', 'points_awarded_teacher',
            'progress_percentage', 'days_remaining',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'learner', 'teacher', 'start_date', 'end_date',
            'points_deducted', 'points_awarded_learner', 'points_awarded_teacher',
            'progress_percentage', 'days_remaining',
            'created_at', 'updated_at'
        )


class SkillRatingSerializer(serializers.ModelSerializer):
    rater = UserSerializer(read_only=True)
    rated_user = UserSerializer(read_only=True)
    learning_session = LearningSessionSerializer(read_only=True)
    skill_name = serializers.CharField(source='learning_session.skill_name', read_only=True)
    
    class Meta:
        model = SkillRating
        fields = (
            'id', 'learning_session', 'rater', 'rated_user',
            'rating', 'feedback', 'skill_name', 'created_at'
        )
        read_only_fields = ('learning_session', 'rater', 'rated_user', 'skill_name', 'created_at')


class BadgeSerializer(serializers.ModelSerializer):
    badge_name = serializers.CharField(source='get_badge_type_display', read_only=True)
    icon = serializers.CharField(source='badge_icon', read_only=True)
    
    class Meta:
        model = Badge
        fields = ('id', 'badge_type', 'badge_name', 'icon', 'earned_at')
        read_only_fields = ('id', 'badge_type', 'badge_name', 'icon', 'earned_at')
