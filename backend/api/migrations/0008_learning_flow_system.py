# Generated migration for learning flow system

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_notification'),
    ]

    operations = [
        migrations.CreateModel(
            name='PointConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('value', models.IntegerField()),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserPoints',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.IntegerField(default=0)),
                ('total_earned', models.IntegerField(default=0)),
                ('total_spent', models.IntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='points', to='auth.user')),
            ],
            options={
                'db_table': 'api_userpoints',
            },
        ),
        migrations.CreateModel(
            name='PointTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('join_learning', 'Join Learning'), ('complete_learning_learner', 'Complete Learning (Learner)'), ('complete_learning_teacher', 'Complete Learning (Teacher)'), ('bonus', 'Bonus'), ('penalty', 'Penalty')], max_length=50)),
                ('amount', models.IntegerField()),
                ('balance_after', models.IntegerField()),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='point_transactions', to='auth.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='LearningSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill_name', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='in_progress', max_length=20)),
                ('total_days', models.IntegerField()),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('points_deducted', models.IntegerField()),
                ('points_awarded_learner', models.IntegerField(blank=True, null=True)),
                ('points_awarded_teacher', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('learner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_sessions_as_learner', to='auth.user')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_sessions_as_teacher', to='auth.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SkillRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField()),
                ('feedback', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('learning_session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='api.learningsession')),
                ('rated_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings_received', to='auth.user')),
                ('rater', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings_given', to='auth.user')),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('learning_session', 'rater')},
            },
        ),
    ]
