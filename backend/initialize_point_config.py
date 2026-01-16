"""
Script to initialize point configuration values
Run this after migration to set up default point values
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import PointConfiguration


def initialize_point_configs():
    """Initialize default point configuration values"""
    
    configs = [
        {
            'name': 'join_learning_cost',
            'value': 100,
            'description': 'Points deducted when a user joins a learning session'
        },
        {
            'name': 'learning_completion_reward_learner',
            'value': 50,
            'description': 'Points awarded to learner upon completing a learning session'
        },
        {
            'name': 'learning_completion_reward_teacher',
            'value': 150,
            'description': 'Points awarded to teacher upon completing a learning session'
        },
        {
            'name': 'default_learning_period_days',
            'value': 30,
            'description': 'Default duration for learning sessions in days'
        },
        {
            'name': 'initial_user_points',
            'value': 1000,
            'description': 'Initial points awarded to new users'
        }
    ]
    
    for config_data in configs:
        config, created = PointConfiguration.objects.get_or_create(
            name=config_data['name'],
            defaults={
                'value': config_data['value'],
                'description': config_data['description']
            }
        )
        if created:
            print(f"✓ Created: {config.name} = {config.value}")
        else:
            print(f"- Already exists: {config.name} = {config.value}")
    
    print(f"\n✓ Point configuration initialized successfully!")


if __name__ == '__main__':
    initialize_point_configs()
