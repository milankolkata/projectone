from django import forms
from .models import Employee, Attendance
from django.utils import timezone
from django.core.exceptions import ValidationError


# class EmployeeForm(forms.ModelForm):
#     class Meta:
#         model = Employee
#         fields = ['first_name', 'last_name', 'email', 'team_code', 'phone_number', 'date_of_birth', 'position', 'salary']

class EmployeeForm(forms.ModelForm):
    first_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"First Name", "class": "form-control"}), label = '')
    last_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Last Name", "class": "form-control"}), label = '')
    email = forms.EmailField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Email", "class": "form-control"}), label = '')
    phone_number = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Phone", "class": "form-control"}), label = '')
    address = forms.CharField(required=True, widget=forms.widgets.Textarea(attrs={"placeholder":"Address", "class": "form-control"}), label = '')
    city = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"City", "class": "form-control"}), label = '')
    state = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"State", "class": "form-control"}), label = '')
    zipcode = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Zip Code", "class": "form-control"}), label = '')
    date_of_birth = forms.CharField(required=True, widget=forms.widgets.TimeInput(attrs={"placeholder":"Date of Birth", "class": "form-control"}), label = '')
    position = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Position", "class": "form-control"}), label = '')
    salary = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Salary", "class": "form-control"}), label = '')
    skills = forms.CharField(required=True, widget=forms.widgets.Textarea(attrs={"placeholder":"Skill-Set", "class": "form-control"}), label = '')
    advances = forms.IntegerField(required=False, widget=forms.widgets.TextInput(attrs={"placeholder":"Advance Taken", "class": "form-control"}), label = '')
    class Meta:
        model = Employee
        exclude = ('user',)

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

    date = forms.DateField(
        initial=timezone.now().date(),
        required=False,
        widget=forms.HiddenInput()  # or use a visible input field
    )

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        date = cleaned_data.get('date')

        if employee and date:
            # Check if an attendance record already exists for this employee on the given date
            if Attendance.objects.filter(employee=employee, date=date).exists():
                raise ValidationError(
                    f"Attendance for {employee} on {date} already exists."
                )

        return cleaned_data