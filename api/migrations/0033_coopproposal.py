# Generated by Django 4.2.9 on 2024-05-14 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0032_newspost_header'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoopProposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.CharField(max_length=70)),
                ('proposal', models.TextField()),
                ('email', models.EmailField(max_length=254)),
                ('telegram', models.CharField(blank=True, max_length=30, null=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
