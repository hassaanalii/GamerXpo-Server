# Generated by Django 4.2.7 on 2023-12-01 11:03

from django.db import migrations, models
import django.db.models.deletion
import xpoarena.models


class Migration(migrations.Migration):

    dependencies = [
        ('xpoarena', '0003_alter_booth_image_alter_booth_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('release_date', models.DateField()),
                ('game_iframe_src', models.URLField(max_length=1000)),
                ('genre', models.CharField(choices=[('RPG', 'Role Playing Game'), ('Action', 'Action'), ('Adventure', 'Adventure'), ('Puzzle', 'Puzzle'), ('Sports', 'Sports'), ('Casual', 'Causal')], default='RPG', max_length=255)),
                ('game_description', models.TextField()),
                ('image_url', models.URLField(max_length=1000)),
                ('last_updated', models.DateField(auto_now=True)),
                ('technology', models.CharField(choices=[('HTML5', 'HTML5'), ('Unity', 'Unity'), ('Unreal Engine', 'Unreal Engine'), ('Cocos2d', 'Cocos2d'), ('Godot', 'Godot')], default='HTML5', max_length=50)),
                ('system_requirements', models.TextField(blank=True, null=True)),
                ('game_trailer', models.FileField(blank=True, null=True, upload_to=xpoarena.models.upload_to)),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('game_download_link', models.URLField(max_length=1000)),
                ('booth', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games', to='xpoarena.booth')),
            ],
        ),
        migrations.CreateModel(
            name='GameScreenshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('screenshot', models.ImageField(blank=True, null=True, upload_to=xpoarena.models.upload_to, verbose_name='Screenshot')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='screenshots', to='xpoarena.game')),
            ],
        ),
    ]
