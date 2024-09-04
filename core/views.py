from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import *
from .models import Employee, Attendance, Individual_Attendance
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone
from datetime import date, time
from django.core.exceptions import ValidationError
from .decorators import allowed_users
from django.contrib import messages
from datetime import date, datetime
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone

# Employee Selection Form
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

# Add Employee View
def add_employee(request):
    form = EmployeeForm(request.POST or None)
    if request.user.is_authenticated:
        if request.method == 'POST':
            if form.is_valid():
                add_employee = form.save()
                messages.success(request, "Record added")
                return redirect('home')
        return render(request, 'add_employee.html', {"form": form})
    else:
        return redirect('login_user')

# Admin Placeholder
def adminn(request):
    return HttpResponse("hi")

# Login User View
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['Password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            user_groups = user.groups.all()  # Access the authenticated user's groups
            for group in user_groups:
                if group.name == 'employees':
                    login(request, user)
                    messages.success(request, 'Login Successful')
                    return redirect('user_attendance')
            else:
                login(request, user)
                messages.success(request, 'Login Successful')
                return redirect('home')
        else:
            messages.error(request, 'Error in Login, Please Try Again')
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')

# Logout User View
def logout_user(request):
    logout(request)
    messages.success(request, 'Logout Successful')
    return redirect('login_user')

def employee_details(request):
    employees = Employee.objects.all()
    return render(request, 'employee_details.html', {'employees': employees})

# Individual Employee Details
def individual_employee_details(request, pk):
    if request.user.is_authenticated:
        # Use `pk` to filter by employee's primary key (id)
        employee = get_object_or_404(Employee, id=pk)
        return render(request, 'individual_employee_details.html', {'employee': employee})
    else:
        messages.success(request, 'Please Login to view individual Record')
        return redirect('login_user')

def select_employee(request):
    employees = Employee.objects.all()

    if request.method == "POST":
        form = EmployeeSelectionForm(request.POST)

        if form.is_valid():
            employee = form.cleaned_data['employee']
            attendance_status = form.cleaned_data['attendance_status']
            today = date.today()

            # Query attendance for the specific employee for the current day
            attendance_for_day = Attendance.objects.filter(employee=employee, date=today).first()

            if attendance_for_day:
                # If attendance exists for today
                messages.warning(request, f"Attendance for {employee} has already been marked")
            else:
                # Create new attendance record
                new_attendance = Attendance(
                    employee=employee,
                    status=attendance_status,
                    date=today
                )
                new_attendance.save()
                messages.success(request, f"Attendance recorded successfully for {employee}")
            
            return redirect('select_employee')
        else:
            print(form.errors)
    else:
        form = EmployeeSelectionForm()

    return render(request, 'record_attendance.html', {'form': form, 'employees': employees})

# User Attendance View
def user_attendance(request):
    current_time = timezone.now()


    user_instance = Employee.objects.get(user_name__iexact=request.user.username)
    # except ObjectDoesNotExist:
    #     messages.error(request, "Employee record not found.")
    #     return redirect('some_error_page')  # Redirect to an error page or handle it as needed

    if request.method == 'POST':
        status = request.POST.get('status')
        today_date = current_time.strftime('%d-%m-%Y')
        formatted_time = current_time.strftime('%H:%M:%S')

        attendance_exists = Attendance.objects.filter(employee=user_instance, date=current_time.date()).exists()

        if attendance_exists:
            messages.warning(request, f"Attendance for {request.user.username} has already been marked for today.")
        else:
            Attendance.objects.create(
                employee=user_instance,
                status=status,
                date=current_time.date(),
                time=current_time.time()
            )
            messages.success(request, f"Attendance recorded successfully for {request.user.username} on {today_date} at {formatted_time}.")

        return redirect('user_attendance')

    context = {
        'current_date': current_time.date(),
        'current_time': current_time.strftime('%H:%M:%S'),
    }

    return render(request, 'user_attendance.html', context)

# Attendance Helper Functions
def get_today_attendance():
    today = date.today()
    return Attendance.objects.filter(date=today)

def absent_today():
    attendance_records = get_today_attendance()
    print(attendance_records)
    print('hi')
    absent_employees = attendance_records.filter(status='absent')
    return absent_employees

def present_today():
    attendance_records = get_today_attendance()
    present_employees = attendance_records.filter(status='present')
    return present_employees

def late_today():
    late_time_threshold = time(11, 30)
    attendance_records = get_today_attendance().filter(status='present')
    late_employees = attendance_records.filter(time__gt=late_time_threshold)
    return late_employees

def on_time_today():
    late_time_threshold = time(11, 30)
    attendance_records = get_today_attendance().filter(status='present')
    on_time_employees = attendance_records.filter(time__lte=late_time_threshold)
    return on_time_employees

# Home View
def home(request):
    attendance_data = get_today_attendance()
    absent_employees = absent_today()
    present_employees = present_today()
    on_time_employees = on_time_today()
    late_employees = late_today()
    return render(
        request,
        'home.html',
        {
            'attendance': attendance_data,
            'present_today': present_employees,
            'absent_today': absent_employees,
            'late_today': late_employees,
            'on_time_today': on_time_employees
        }
    )

# QR Code Generation
def dynamic_qr(request):
    random_number = '290901'
    today_date = datetime.now().strftime('%d%m%y')
    domain = 'milankolkata.com'
    data = f"https://{domain}/{random_number}{today_date}"

    # Create a QR code object
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Add data to the QR code
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill='black', back_color='white')

    # Save the image to a BytesIO object
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    file_name = f'qrcode_{domain}_{today_date}.png'
    file_path = default_storage.save(f'qr_codes/{file_name}', ContentFile(img_io.getvalue()))

    file_url = f"{settings.MEDIA_URL}qr_codes/{file_name}"

    return render(request, 'attendance_qr.html', {'file_path': file_url})

# Attendance Views
def today_present(request):
    present_employees = present_today()
    employees = Employee.objects.all()
    return render(request, 'today_present.html', {'today_present': present_employees, 'employees': employees})

def today_absent(request):
    absent_employees = absent_today()
    return render(request, 'today_absent.html', {'today_absent': absent_employees})

def today_on_time(request):
    on_time_employees = on_time_today()
    return render(request, 'today_on_time.html', {'today_on_time': on_time_employees})

def today_late(request):
    late_employees = late_today()
    return render(request, 'today_late.html', {'today_late': late_employees})
