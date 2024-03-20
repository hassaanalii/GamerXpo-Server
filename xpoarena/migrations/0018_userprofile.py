# Generated by Django 4.2.7 on 2024-03-20 12:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import xpoarena.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('xpoarena', '0017_game_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=50)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to=xpoarena.models.upload_to)),
                ('profile_picture_url', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
