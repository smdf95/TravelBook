# Generated by Django 5.0 on 2024-03-12 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_profile_first_name_remove_profile_last_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='f_name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='profile',
            name='l_name',
            field=models.CharField(default='', max_length=100),
        ),
    ]
