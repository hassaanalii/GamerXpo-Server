# Generated by Django 4.2.7 on 2023-12-12 20:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xpoarena', '0010_alter_theme_theme_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoothCustomization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('background_color', models.CharField(max_length=7)),
                ('font_color', models.CharField(max_length=7)),
                ('booth', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='customization', to='xpoarena.booth')),
                ('theme', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='booths', to='xpoarena.theme')),
            ],
        ),
    ]
