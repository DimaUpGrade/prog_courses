# Generated by Django 4.2.9 on 2024-05-15 23:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_delete_coopproposal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newspost',
            name='likes',
        ),
    ]
