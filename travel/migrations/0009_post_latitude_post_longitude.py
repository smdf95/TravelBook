# Generated by Django 5.0 on 2024-03-26 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0008_comment_reply'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
