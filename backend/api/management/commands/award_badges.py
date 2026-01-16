from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import LearningSession, Badge, Notification
from django.db.models import Count, Q


class Command(BaseCommand):
    help = 'Retroactively award badges to users based on their completed learning sessions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Award badges to a specific user (optional)',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        
        if username:
            try:
                users = [User.objects.get(username=username)]
                self.stdout.write(f'Processing badges for user: {username}')
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
                return
        else:
            users = User.objects.all()
            self.stdout.write(f'Processing badges for all {users.count()} users...')
        
        total_badges_awarded = 0
        
        for user in users:
            badges_awarded = self.award_user_badges(user)
            if badges_awarded > 0:
                total_badges_awarded += badges_awarded
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ {user.username}: Awarded {badges_awarded} badge(s)'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Complete! Awarded {total_badges_awarded} badges total.'
            )
        )

    def award_user_badges(self, user):
        """Award badges to a single user based on their completed sessions"""
        badges_awarded = 0
        
        # Count unique skills learned (as learner)
        learner_count = LearningSession.objects.filter(
            learner=user,
            status='completed'
        ).values('skill_name').distinct().count()
        
        # Count unique skills taught (as teacher)
        teacher_count = LearningSession.objects.filter(
            teacher=user,
            status='completed'
        ).values('skill_name').distinct().count()
        
        # Define badge thresholds
        learner_badges = [
            (3, 'learner_3'),
            (5, 'learner_5'),
            (10, 'learner_10'),
        ]
        
        teacher_badges = [
            (3, 'teacher_3'),
            (5, 'teacher_5'),
            (10, 'teacher_10'),
        ]
        
        # Award learner badges
        for threshold, badge_type in learner_badges:
            if learner_count >= threshold:
                badge, created = Badge.objects.get_or_create(
                    user=user,
                    badge_type=badge_type
                )
                if created:
                    badges_awarded += 1
                    # Create notification
                    Notification.objects.create(
                        user=user,
                        notification_type='skill_match',
                        title='🏆 Badge Awarded!',
                        message=f'You earned the "{badge.get_badge_type_display()}" badge for completing {learner_count} learning sessions!',
                        link='/profile'
                    )
        
        # Award teacher badges
        for threshold, badge_type in teacher_badges:
            if teacher_count >= threshold:
                badge, created = Badge.objects.get_or_create(
                    user=user,
                    badge_type=badge_type
                )
                if created:
                    badges_awarded += 1
                    # Create notification
                    Notification.objects.create(
                        user=user,
                        notification_type='skill_match',
                        title='🏆 Badge Awarded!',
                        message=f'You earned the "{badge.get_badge_type_display()}" badge for teaching {teacher_count} different skills!',
                        link='/profile'
                    )
        
        return badges_awarded
