# Generated by Django 4.2.10 on 2024-05-29 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0012_alter_matches_innings_id_alter_oversummary_inningsid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matches',
            name='innings_id',
            field=models.CharField(default=1, max_length=10, null=True),
        ),
    ]
