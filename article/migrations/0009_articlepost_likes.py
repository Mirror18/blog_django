# Generated by Django 2.2 on 2024-01-25 01:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0008_delete_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepost',
            name='likes',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
