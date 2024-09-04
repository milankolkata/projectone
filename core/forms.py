from django import forms
from .models import Employee, Attendance
from django.utils import timezone
from django.core.exceptions import ValidationError


# class EmployeeForm(forms.ModelForm):
#     class Meta:
#         model = Employee
#         fields = ['first_name', 'last_name', 'email', 'team_code', 'phone_number', 'date_of_birth', 'position', 'salary']

class EmployeeForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={"placeholder":"First Name", "class": "form-control"}), 
        label=''
    )
    last_name = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={"placeholder":"Last Name", "class": "form-control"}), 
        label=''
    )
    username = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={"placeholder":"Username", "class": "form-control"}), 
        label=''
    )
    password = forms.CharField(
        required=True, 
        widget=forms.PasswordInput(attrs={"placeholder":"Password", "class": "form-control"}), 
        label=''
    )
    phone_number = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={"placeholder":"Phone", "class": "form-control"}), 
        label=''
    )
    address = forms.CharField(
        required=True, 
        widget=forms.Textarea(attrs={"placeholder":"Address", "class": "form-control"}), 
        label=''
    )
    date_of_birth = forms.DateField(
        required=True, 
        widget=forms.DateInput(attrs={"placeholder":"Date of Birth", "class": "form-control", "type": "date"}), 
        label=''
    )
    position = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={"placeholder":"Position", "class": "form-control"}), 
        label=''
    )
    salary = forms.IntegerField(
        required=True, 
        widget=forms.NumberInput(attrs={"placeholder":"Salary", "class": "form-control"}), 
        label=''
    )
    skills = forms.CharField(
        required=True, 
        widget=forms.Textarea(attrs={"placeholder":"Skill-Set", "class": "form-control"}), 
        label=''
    )
    advances = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={"placeholder":"Advance Taken", "class": "form-control"}), 
        label=''
    )
    
    class Meta:
        model = Employee
        exclude = ('user',)

# atteandamce
# atteandamce
class EmployeeSelectionForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        label="Select an Employee",
        empty_label="Choose an employee"
    )
    
    attendance_status = forms.ChoiceField(
        choices=[('present', 'Present'), ('absent', 'Absent')],
        widget=forms.RadioSelect,
        label="Attendance Status"
    )

# class User_attendanceForm(forms.Form):
