# Generated by Django 4.2.7 on 2024-05-14 18:09

from django.db import migrations, models
import django.db.models.deletion
import xpoarena.models


class Migration(migrations.Migration):

    dependencies = [
        ('xpoarena', '0028_gamefeedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='bronze_sponsor',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='gold_sponsor',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='silver_sponsor',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Sponsorship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('package', models.CharField(choices=[('Gold', 'Gold'), ('Silver', 'Silver'), ('Bronze', 'Bronze')], max_length=10)),
                ('name', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('details', models.TextField()),
                ('logo', models.ImageField(upload_to=xpoarena.models.upload_to)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sponsorships', to='xpoarena.event')),
            ],
        ),
    ]
