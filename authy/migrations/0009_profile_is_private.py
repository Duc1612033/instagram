# Generated by Django 5.1.2 on 2024-11-19 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authy', '0008_profile_blocked_friends'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_private',
            field=models.BooleanField(default=False),
        ),
    ]
