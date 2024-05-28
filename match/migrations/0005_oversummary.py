# Generated by Django 4.2.10 on 2024-05-27 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0004_matches_start_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='OverSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_id', models.CharField(max_length=100, null=True)),
                ('InningsId', models.CharField(max_length=100, null=True)),
                ('OverNum', models.CharField(max_length=100, null=True)),
                ('Event', models.CharField(max_length=100, null=True)),
                ('commentary', models.CharField(max_length=300, null=True)),
            ],
        ),
    ]