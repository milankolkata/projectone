# Generated by Django 5.1 on 2024-09-04 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_employee_user_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='time',
            field=models.TimeField(),
        ),
    ]
