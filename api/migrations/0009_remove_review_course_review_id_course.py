# Generated by Django 4.2.9 on 2024-01-31 20:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_remove_course_reviews_review_course'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='course',
        ),
        migrations.AddField(
            model_name='review',
            name='id_course',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='api.course'),
            preserve_default=False,
        ),
    ]
