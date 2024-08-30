from django import forms
from .models import Employee, Attendance

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