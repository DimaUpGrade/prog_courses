# Generated by Django 4.2.9 on 2024-04-25 23:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_course_cost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='cost',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
    ]
