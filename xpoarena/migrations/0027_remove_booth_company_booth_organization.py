# Generated by Django 4.2.7 on 2024-05-12 18:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('xpoarena', '0026_conversation_conversationmessage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booth',
            name='company',
        ),
        migrations.AddField(
            model_name='booth',
            name='organization',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='xpoarena.organization'),
        ),
    ]
