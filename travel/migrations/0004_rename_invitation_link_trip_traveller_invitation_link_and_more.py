# Generated by Django 5.0 on 2024-03-30 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0003_trip_invitation_link'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trip',
            old_name='invitation_link',
            new_name='traveller_invitation_link',
        ),
        migrations.AddField(
            model_name='trip',
            name='viewer_invitation_link',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
    ]