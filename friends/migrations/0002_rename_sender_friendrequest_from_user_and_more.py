# Generated by Django 5.1.2 on 2024-10-29 17:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('friends', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='friendrequest',
            old_name='sender',
            new_name='from_user',
        ),
        migrations.RenameField(
            model_name='friendrequest',
            old_name='receiver',
            new_name='to_user',
        ),
        migrations.RemoveField(
            model_name='friendrequest',
            name='accepted',
        ),
    ]
