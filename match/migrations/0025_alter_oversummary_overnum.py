# Generated by Django 4.2.10 on 2024-10-31 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0024_alter_oversummary_commentary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oversummary',
            name='OverNum',
            field=models.FloatField(max_length=100, null=True),
        ),
    ]
