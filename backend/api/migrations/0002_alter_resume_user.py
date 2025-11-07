from django.db import migrations, models
from django.db import migrations, models


def remove_duplicate_resumes(apps, schema_editor):
    Resume = apps.get_model('api', 'Resume')

    # Get all user IDs who have more than one resume
    user_ids = Resume.objects.values_list('user_id', flat=True).distinct()

    for user_id in user_ids:
        resumes = Resume.objects.filter(user_id=user_id).order_by('-created_at')
        # Keep only the most recent resume
        if resumes.count() > 1:
            resumes.exclude(id=resumes.first().id).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_duplicate_resumes),
        migrations.AlterField(
            model_name='resume',
            name='user',
            field=models.OneToOneField(on_delete=models.deletion.CASCADE, related_name='resume', to='auth.user'),
        ),
    ]