from django.db import models
from django.utils import timezone

class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=False)
    team_code = models.AutoField(primary_key=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    skills = models.CharField(max_length=500)
    advances = models.IntegerField(default=0)
    def __str__(self):
        return(f"{self.first_name} {self.last_name}")


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now=True)
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, default='Check')

    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} - {self.status} on {self.date} - {self.time}"

