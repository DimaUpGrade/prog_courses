# Generated by Django 4.2.9 on 2024-01-31 20:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_remove_review_course_course_rewies_course_users_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='rewies',
            new_name='reviews',
        ),
    ]
