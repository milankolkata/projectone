from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import pytz

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
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
        ('absent', 'Absent'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)  # Defaults to today
    time = models.TimeField(default=timezone.localtime)  # Converts to local time before saving
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, default='Check')

    def save(self, *args, **kwargs):
        # Convert UTC time to local time (IST) before saving
        self.time = timezone.localtime(self.time, pytz.timezone('Asia/Kolkata')).time()
        super().save(*args, **kwargs)

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
    
