# Generated by Django 4.2.9 on 2024-05-18 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0037_remove_newspost_likes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='course_tags', to='api.tag'),
        ),
    ]
