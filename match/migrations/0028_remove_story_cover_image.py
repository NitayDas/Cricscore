# Generated by Django 4.2.10 on 2024-11-30 08:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0027_alter_oversummary_overnum'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='story',
            name='cover_image',
        ),
    ]
