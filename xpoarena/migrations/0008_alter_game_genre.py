# Generated by Django 4.2.7 on 2023-12-01 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xpoarena', '0007_alter_game_genre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='genre',
            field=models.CharField(choices=[('Action', 'Action'), ('Adventure', 'Adventure'), ('Puzzle', 'Puzzle'), ('Sports', 'Sports'), ('Casual', 'Causal'), ('Shooting', 'Shooting'), ('Driving', 'Driving')], default='RPG', max_length=255),
        ),
    ]
