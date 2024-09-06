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
def user_attendance(request, date):
    current_time = timezone.now()
    user_name = request.user.username
    print(user_name)

    # Convert the date from URL to a datetime object
    try:
        date_from_url = datetime.strptime(date, '%d%m%y').date()  # Assuming date in 'ddmmyy' format
    except ValueError:
        messages.error(request, "Invalid date format.")
        return render(request, 'user_attendance.html', {})

    # Get the current user's Employee instance
    try:
        user_instance = Employee.objects.get(user_name=user_name)
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found.")
        return render(request, 'user_attendance.html', {})

    if request.method == 'POST':
        status = request.POST.get('status')

        # Check if attendance has already been marked for the given date
        attendance_exists = Attendance.objects.filter(employee=user_instance, date=date_from_url).exists()

        if attendance_exists:
            messages.warning(request, f"Attendance for {request.user.username} has already been marked for {date_from_url}.")
        else:
            # Use timezone-aware time and save attendance for the given date
            Attendance.objects.create(
                employee=user_instance,
                status=status,
                date=date_from_url,
                time=current_time,  # Save the full timezone-aware datetime here
            )
            formatted_time = current_time.strftime('%H:%M:%S')
            messages.success(request, f"Attendance recorded successfully for {request.user.username} on {date_from_url} at {formatted_time}.")
        return render(request, 'user_attendance.html', {})

    context = {
        'current_date': current_time.date(),
        'current_time': current_time.strftime('%H:%M:%S'),
        'date_from_url': date_from_url,
    }

    return render(request, 'user_attendance.html', context)


# Attendance Helper Functions
def get_today_attendance():
    today = date.today()
    return Attendance.objects.filter(date=today)

def absent_today():
    attendance_records = get_today_attendance()
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
    print(on_time_employees)
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
def today_date_func():
    today_date = datetime.now().strftime('%d%m%y')
    return today_date


def dynamic_qr(request):
    random_number = '290901'
    todays_date = today_date_func()  # Assuming this function returns the date in 'ddmmyy' format
    domain = 'milankolkata.com'
    data = f"https://{domain}/user{random_number}{todays_date}"

    # Define file name and path
    file_name = f'qrcode_{domain}_{todays_date}.png'
    file_path = f'qr_codes/{file_name}'
    
    # Check if QR code already exists for today
    if not default_storage.exists(file_path):
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

        # Save the file to the storage only if it doesn't exist
        default_storage.save(file_path, ContentFile(img_io.getvalue()))

    # Generate the file URL
    file_url = f"{settings.MEDIA_URL}qr_codes/{file_name}"

    # Get current date, time, and day
    current_date_time = timezone.now().strftime('%A, %d %B %Y, %H:%M:%S')

    # Pass the file URL and the current date and time to the template
    return render(request, 'attendance_qr.html', {
        'file_path': file_url,
        'current_date_time': current_date_time,
    })

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
    print(on_time_employees)
    return render(request, 'today_on_time.html', {'today_on_time': on_time_employees})

def today_late(request):
    late_employees = late_today()
    return render(request, 'today_late.html', {'today_late': late_employees})
