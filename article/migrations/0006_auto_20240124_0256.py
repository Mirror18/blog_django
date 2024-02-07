# Generated by Django 2.2 on 2024-01-23 18:56

import ckeditor.fields
from django.db import migrations, models
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0005_articlepost_avatar'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', ckeditor.fields.RichTextField()),
            ],
        ),
        migrations.AlterField(
            model_name='articlepost',
            name='avatar',
            field=imagekit.models.fields.ProcessedImageField(upload_to='article/%Y%m%d'),
        ),
    ]
