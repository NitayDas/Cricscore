# Generated by Django 4.2.10 on 2024-04-29 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0002_matches_flag1_matches_flag2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matches',
            name='status',
            field=models.CharField(max_length=100, null=True),
        ),
    ]