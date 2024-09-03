from django.db import migrations, models

def set_default_user_name(apps, schema_editor):
    Employee = apps.get_model('core', 'Employee')
    Employee.objects.filter(user_name__isnull=True).update(user_name='default_user_name')

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_attendance_time_individual_attendance'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='user_name',
            field=models.CharField(max_length=50, default='default_user_name'),
        ),
        migrations.RunPython(set_default_user_name),
    ]
