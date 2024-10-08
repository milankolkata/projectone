from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import pytz

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    user_name = models.CharField(max_length=25, default='default_user_name')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    address = models.TextField(default='Kolkata')
    date_of_birth = models.DateField()
    position = models.CharField(max_length=100)
    salary = models.IntegerField()
    skills = models.TextField()
    advances = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"




class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),  # Add 'Absent' as a choice to align with the default
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)  # Defaults to today
    time = models.TimeField(auto_now_add=True)  # Converts to local time before saving
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, default='absent')

    class Meta:
        unique_together = ('employee', 'date')  # Ensure unique attendance for each employee per day

    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} - {self.status} on {self.date} - {self.time}"
    
    

class Individual_Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')

    def __str__(self):
        return f"{self.employee.user_name} - {self.status} on {self.date} at {self.time}"
    
