# Generated by Django 4.2.10 on 2024-11-02 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0026_alter_oversummary_overnum'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oversummary',
            name='OverNum',
            field=models.FloatField(max_length=100, null=True),
        ),
    ]
