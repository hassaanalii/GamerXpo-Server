# Generated by Django 4.2.7 on 2023-12-13 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xpoarena', '0014_alter_game_genre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='image_url',
            field=models.CharField(max_length=1000),
        ),
    ]
