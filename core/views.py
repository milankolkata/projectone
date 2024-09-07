from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import EmployeeForm, EmployeeSelectionForm
from .models import Employee, Attendance
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from django.core.files.storage import default_storage
from io import BytesIO
from django.core.files.base import ContentFile
import qrcode
from django.conf import settings
from datetime import date, time

# Helper Functions
def get_today_attendance():
    today = timezone.now().date()
    return Attendance.objects.filter(date=today).select_related('employee')

def mark_all_absent():
    today = timezone.now().date()
    employees_without_attendance = Employee.objects.exclude(attendance__date=today)
    new_attendances = [
        Attendance(employee=employee, date=today, status='absent')
        for employee in employees_without_attendance
    ]
    Attendance.objects.bulk_create(new_attendances)

def present_today():
    return get_today_attendance().filter(status='present')

def absent_today():
    mark_all_absent()
    return get_today_attendance().filter(status='absent')

def late_today():
    late_time_threshold = time(11, 30)
    return get_today_attendance().filter(status='present', time__gt=late_time_threshold)

def on_time_today():
    late_time_threshold = time(11, 30)
    return get_today_attendance().filter(status='present', time__lte=late_time_threshold)

# Views
def add_employee(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    
    form = EmployeeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Record added")
        return redirect('home')
    
    return render(request, 'add_employee.html', {"form": form})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['Password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Login Successful')
            return redirect('employee_landing_pages/user_attendance' if user.groups.filter(name='employees').exists() else 'home')
        else:
            messages.error(request, 'Error in Login, Please Try Again')
    
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    messages.success(request, 'Logout Successful')
    return redirect('login_user')

def employee_details(request):
    employees = Employee.objects.all()
    return render(request, 'employee_details.html', {'employees': employees})

def individual_employee_details(request, pk):
    if not request.user.is_authenticated:
        messages.success(request, 'Please Login to view individual Record')
        return redirect('login_user')
    
    employee = get_object_or_404(Employee, id=pk)
    return render(request, 'individual_employee_details.html', {'employee': employee})

def select_employee(request):
    employees = Employee.objects.all()

    if request.method == "POST":
        form = EmployeeSelectionForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            attendance_status = form.cleaned_data['attendance_status']
            today = date.today()

            if not Attendance.objects.filter(employee=employee, date=today).exists():
                Attendance.objects.create(employee=employee, status=attendance_status, date=today)
                messages.success(request, f"Attendance recorded for {employee}")
            else:
                messages.warning(request, f"Attendance for {employee} already marked")

            return redirect('select_employee')
    else:
        form = EmployeeSelectionForm()

    return render(request, 'record_attendance.html', {'form': form, 'employees': employees})

# Main attendance function that processes user attendance based on the date passed in the URL
def user_attendance(request, date_str):
    current_time = timezone.now()
    user_name = request.user.username
    
    # Convert the date from URL to a datetime object
    try:
        date_from_url = datetime.strptime(date_str, '%d%m%y').date()  # Assuming date in 'ddmmyy' format
    except ValueError:
        messages.error(request, "Invalid date format.")
        return render(request, 'employee_landing_pages/user_attendance.html', {})

    # Get the current user's Employee instance
    try:
        user_instance = Employee.objects.get(user_name=user_name)
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found.")
        return render(request, 'employee_landing_pages/user_attendance.html', {})

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
        return render(request, 'employee_landing_pages/user_attendance.html', {})

    context = {
        'current_date': current_time.date(),
        'current_time': current_time.strftime('%H:%M:%S'),
        'date_from_url': date_from_url,
    }

    return render(request, 'employee_landing_pages/user_attendance.html', context)

# Home View
def home(request):
    return render(request, 'home.html', {
        'attendance': get_today_attendance(),
        'present_today': present_today(),
        'absent_today': absent_today(),
        'late_today': late_today(),
        'on_time_today': on_time_today(),
    })

# QR Code Generation
def dynamic_qr(request):
    todays_date = datetime.now().strftime('%d%m%y')
    domain = 'milankolkata.com'
    data = f"https://{domain}/user290901{todays_date}"

    file_name = f'qrcode_{domain}_{todays_date}.png'
    file_path = f'qr_codes/{file_name}'

    if not default_storage.exists(file_path):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        default_storage.save(file_path, ContentFile(img_io.getvalue()))

    file_url = f"{settings.MEDIA_URL}qr_codes/{file_name}"
    current_date_time = timezone.now().strftime('%A, %d %B %Y, %H:%M:%S')

    return render(request, 'attendance_qr.html', {
        'file_path': file_url,
        'current_date_time': current_date_time,
    })

# Attendance Status Views
def today_present(request):
    return render(request, 'today_present.html', {'today_present': present_today()})

def today_absent(request):
    return render(request, 'today_absent.html', {'today_absent': absent_today()})

def today_on_time(request):
    return render(request, 'today_on_time.html', {'today_on_time': on_time_today()})

def today_late(request):
    return render(request, 'today_late.html', {'today_late': late_today()})
