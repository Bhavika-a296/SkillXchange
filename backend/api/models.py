from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    # Keep the default `id` primary key in SQLite (more robust for migrations).
    # Make `user` a OneToOneField to enforce uniqueness, but do NOT make it the PK here.
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_userprofile'  # Explicitly set table name

    def __str__(self):
        return f"{self.user.username}'s profile"

class Skill(models.Model):
    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    proficiency_level = models.CharField(
        max_length=20,
        choices=PROFICIENCY_CHOICES,
        default='beginner'
    )
    # Store the BERT embedding as a JSON array
    embedding = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class Resume(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resume')
    file = models.FileField(upload_to='resumes/')
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s resume"

class SkillMatch(models.Model):
    seeker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skill_matches_as_seeker')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skill_matches_as_provider')
    desired_skill = models.CharField(max_length=100)
    similarity_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-similarity_score']

    def __str__(self):
        return f"{self.seeker.username} -> {self.provider.username} ({self.desired_skill})"


class Connection(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('connected', 'Connected'),
        ('rejected', 'Rejected'),
    ]

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connections_requested')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connections_received')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('requester', 'receiver')

    def __str__(self):
        return f"{self.requester.username} -> {self.receiver.username} ({self.status})"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_received')
    content = models.TextField()
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.content[:30]}"


class DailyLogin(models.Model):
    """Track daily logins for streak calculation"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_logins')
    login_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'login_date')
        ordering = ['-login_date']

    def __str__(self):
        return f"{self.user.username} - {self.login_date}"


class Notification(models.Model):
    """Store notifications for users"""
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),
        ('connection_request', 'Connection Request'),
        ('connection_accepted', 'Connection Accepted'),
        ('skill_match', 'Skill Match Found'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_sent', null=True, blank=True)
    link = models.CharField(max_length=500, blank=True)  # URL to navigate to
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.notification_type}: {self.title}"


class PointConfiguration(models.Model):
    """Configurable point values for the learning system"""
    name = models.CharField(max_length=100, unique=True)
    value = models.IntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: {self.value}"


class UserPoints(models.Model):
    """Track user point balance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='points')
    balance = models.IntegerField(default=0)
    total_earned = models.IntegerField(default=0)
    total_spent = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'api_userpoints'

    def __str__(self):
        return f"{self.user.username}: {self.balance} points"


class PointTransaction(models.Model):
    """Track all point transactions"""
    TRANSACTION_TYPES = [
        ('join_learning', 'Join Learning'),
        ('complete_learning_learner', 'Complete Learning (Learner)'),
        ('complete_learning_teacher', 'Complete Learning (Teacher)'),
        ('bonus', 'Bonus'),
        ('penalty', 'Penalty'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    amount = models.IntegerField()  # Positive for addition, negative for deduction
    balance_after = models.IntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.amount} ({self.transaction_type})"


class LearningSession(models.Model):
    """Track learning sessions between users"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]

    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_sessions_as_learner')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_sessions_as_teacher')
    skill_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Learning period configuration
    total_days = models.IntegerField()  # Total learning period in days
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Points tracking
    points_deducted = models.IntegerField()
    points_awarded_learner = models.IntegerField(null=True, blank=True)
    points_awarded_teacher = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.learner.username} learning {self.skill_name} from {self.teacher.username}"

    @property
    def progress_percentage(self):
        """Calculate progress based on elapsed days"""
        from django.utils import timezone
        if self.status == 'completed':
            return 100
        
        elapsed_days = (timezone.now() - self.start_date).days
        if elapsed_days >= self.total_days:
            return 100
        return int((elapsed_days / self.total_days) * 100)

    @property
    def days_remaining(self):
        """Calculate remaining days in learning period"""
        from django.utils import timezone
        if self.status == 'completed':
            return 0
        
        elapsed_days = (timezone.now() - self.start_date).days
        remaining = self.total_days - elapsed_days
        return max(0, remaining)


class SkillRating(models.Model):
    """Store ratings and feedback after learning completion"""
    learning_session = models.ForeignKey(LearningSession, on_delete=models.CASCADE, related_name='ratings')
    rater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')
    rated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_received')
    
    rating = models.IntegerField()  # 1-5 stars
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('learning_session', 'rater')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rater.username} rated {self.rated_user.username}: {self.rating}/5"


class Badge(models.Model):
    """User achievement badges"""
    BADGE_TYPES = [
        ('learner_3', 'Learner - 3 Skills'),
        ('learner_5', 'Learner - 5 Skills'),
        ('learner_10', 'Learner - 10 Skills'),
        ('teacher_3', 'Teacher - 3 Skills'),
        ('teacher_5', 'Teacher - 5 Skills'),
        ('teacher_10', 'Teacher - 10 Skills'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'badge_type')
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_badge_type_display()}"
    
    @property
    def badge_icon(self):
        """Return emoji icon for badge"""
        icons = {
            'learner_3': '📚',
            'learner_5': '🎓',
            'learner_10': '🏆',
            'teacher_3': '👨‍🏫',
            'teacher_5': '🌟',
            'teacher_10': '💫',
        }
        return icons.get(self.badge_type, '🏅')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_user_points(sender, instance, created, **kwargs):
    """Create UserPoints record when a new user is created"""
    if created:
        UserPoints.objects.create(user=instance, balance=1000)  # Starting balance


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """Create a notification when a new message is sent"""
    if created:
        Notification.objects.create(
            user=instance.receiver,
            notification_type='message',
            title=f'New message from {instance.sender.username}',
            message=instance.content[:100],  # First 100 chars of message
            sender=instance.sender,
            link=f'/messages?user={instance.sender.username}'
        )