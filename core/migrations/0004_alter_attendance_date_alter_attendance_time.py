# Generated by Django 5.1 on 2024-09-04 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_attendance_date_alter_attendance_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='time',
            field=models.TimeField(auto_now_add=True),
        ),
    ]
