# Generated by Django 4.2.9 on 2024-02-04 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_remove_course_users_course_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='likes',
            field=models.IntegerField(default=0),
        ),
    ]