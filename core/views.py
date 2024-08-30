from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import *
from .models import Employee, Attendance
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone


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




def home(request):
    attendance_data = Attendance.objects.all()
    return render(request, 'home.html', {'attendance':attendance_data})


def add_employee(request):
    form = EmployeeForm(request.POST or None)
    if request.user.is_authenticated:
        if request.method == 'POST':
            if form.is_valid():
                add_employee = form.save()
                messages.success(request, "Record added")
                return redirect('home')
        return render(request, 'add_employee.html', {"form":form})
    else:
        return redirect('login_user')




def adminn(request):
    return render(request, 'admin.html', {})



def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['Password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'LogIn Successful')
            return redirect('home') 
        else:
            messages.error(request, 'Error in Login, Please Try Again')
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')
 



def logout_user(request):
    logout(request)
    messages.success(request, 'Logout Successful')
    return redirect('login_user')



def employee_details(request):
    employees = Employee.objects.all()
    return render(request,'employee_details.html', {'employees':employees})

def individual_employee_details(request, pk):
    if request.user.is_authenticated:
        employee = Employee.objects.get(team_code=pk)
        return render(request, 'individual_employee_details.html' , {'employee':employee})
    else:
        messages.success(request, 'Please Login to view individual Record')
        return redirect('login_user')


# class AttendanceForm(forms.ModelForm):
#     class Meta:
#         model = Attendance
#         fields = ['employee', 'time_in']
#         widgets = {
#             'time_in': forms.TimeInput(format='%H:%M:%S', attrs={'type': 'time'}),
#         }






# def record_attendance(request):
#     if request.method == 'POST':
#         form = AttendanceForm(request.POST)
#         if form is not None:
#             team_code = request.POST['team_code']
#             attendance =  request.POST['attendance']
#             print(team_code)
#             print(attendance)
#             employee_instance = Employee.objects.get(team_code)
#             attendance_entry = Attendance.objects.create(
#             employee=employee_instance,
#             date=timezone.now().date(),
#             time_in=timezone.now().time(),
#             attendance=attendance  # Replace with the desired attendance status
#             )
#             # Here you would typically save the form data to the database
#             # attendance_record = form.save(commit=False)
#             # attendance_record.save()
#             attendance_entry.save()
#             # attendance_entries = Attendance.objects.all()
#             # for entry in attendance_entries:
#             #     print(f"Employee: {entry.employee}, Date: {entry.date}, Time In: {entry.time_in}, Attendance: {entry.attendance}")

#             messages.success(request, 'Attendance recorded successfully.')
#             return redirect('record_attendance')  # Redirect to a specific view after successful submission
#         else:
#             messages.error(request, 'There was an error recording attendance. Please try again.')
#     else:
#         form = AttendanceForm()
    
#     employees = Employee.objects.all()

#     return render(request, 'record_attendance.html', {'form': form, 'employees': employees})




def select_employee(request):
    employees = Employee.objects.all()
    print('0')
    
    if request.method == "POST":
        print('1')
        form = EmployeeSelectionForm(request.POST)
        if form.is_valid():
            print('2')
            print('Form is valid')  # Debugging: Check if this is reached
            employee  = form.cleaned_data['employee']
            attendance_status = form.cleaned_data['attendance_status']
            
            # Save the attendance record to the database
            attendance = Attendance(
                employee=employee ,
                status=attendance_status
            )
            attendance.save()

            # Show a success message and redirect or render success page
            messages.success(request, f"Attendance recorded successfully for {employee}")
            return redirect('select_employee')  # Replace with your actual success URL or view name
        else:
            print(form.errors)  # Debugging: Print form errors
    else:
        form = EmployeeSelectionForm()
    return render(request, 'record_attendance.html', {'form': form, 'employees': employees})