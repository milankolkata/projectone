# Generated by Django 5.1 on 2024-08-29 09:26

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_record'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='skills',
            field=models.CharField(default=django.utils.timezone.now, max_length=500),
            preserve_default=False,
        ),
    ]
