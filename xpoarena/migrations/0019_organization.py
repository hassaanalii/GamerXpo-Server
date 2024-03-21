# Generated by Django 4.2.7 on 2024-03-21 11:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import xpoarena.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('xpoarena', '0018_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('website_url', models.URLField(blank=True, max_length=255, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(blank=True, max_length=255, null=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to=xpoarena.models.upload_to)),
                ('description', models.TextField(blank=True, null=True)),
                ('founded_date', models.DateField(blank=True, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('created_by', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]