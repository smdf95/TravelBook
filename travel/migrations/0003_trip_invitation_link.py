# Generated by Django 5.0 on 2024-03-30 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0002_trip_date_from_trip_date_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='invitation_link',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
    ]
