# Generated by Django 5.1.2 on 2024-11-13 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friends', '0008_auto_20241113_1343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockeduser',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='friend',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='friendrequest',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
