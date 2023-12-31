# Generated by Django 4.2.7 on 2023-11-23 09:58

from django.db import migrations, models
import xpoarena.models


class Migration(migrations.Migration):

    dependencies = [
        ('xpoarena', '0002_alter_booth_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booth',
            name='image',
            field=models.ImageField(upload_to=xpoarena.models.upload_to, verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='booth',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
