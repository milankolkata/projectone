from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import EmployeeForm, EmployeeSelectionForm
from .models import Employee, Attendance
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, time
from django.core.files.storage import default_storage
from io import BytesIO
from django.core.files.base import ContentFile
import qrcode
from django.conf import settings
import pytz
from django.utils.timezone import localtime
from datetime import time

# Helper function to get attendance based on status and time conditions
def get_attendance_by_status(status=None, late_threshold=None):
    today = timezone.localtime(timezone.now()).date()  # Ensure the same timezone
    attendance_qs = Attendance.objects.filter(date=today).select_related('employee')
    
    if status:
        attendance_qs = attendance_qs.filter(status=status)
    
    if late_threshold is not None:
        if late_threshold:  # late employees
            late_time_threshold = time(11, 30)
            attendance_qs = attendance_qs.filter(time__gt=late_time_threshold)
        else:  # on-time employees
            late_time_threshold = time(11, 30)
            attendance_qs = attendance_qs.filter(time__lte=late_time_threshold)
    
    return attendance_qs

# Views to display attendance statuses
def attendance_status_view(request, status_type):
    today = timezone.now().date()
    late_time_threshold = time(11, 30)

    if status_type == 'present':
        attendance_list = Attendance.objects.filter(date=today, status='present')
    elif status_type == 'absent':
        attendance_list = Attendance.objects.filter(date=today, status='absent')
    elif status_type == 'late':
        attendance_list = Attendance.objects.filter(date=today, status='present', time__gt=late_time_threshold)
    elif status_type == 'on_time':
        # Fetch on-time employees: attendance marked at or before 11:30 AM
        attendance_list = Attendance.objects.filter(date=today, status='present', time__lte=late_time_threshold)
    else:
        attendance_list = []

    template_map = {
        'present': 'today_present.html',
        'absent': 'today_absent.html',
        'late': 'today_late.html',
        'on_time': 'today_on_time.html'
    }

    return render(request, template_map.get(status_type, 'home.html'), {f'today_{status_type}': attendance_list})



def mark_all_absent():
    today = timezone.now().date()
    employees_without_attendance = Employee.objects.exclude(attendance__date=today)
    
    # Collect all new attendance records in a list
    new_attendances = [
        Attendance(employee=employee, date=today, status='absent')
        for employee in employees_without_attendance
    ]
    
    # Create the new attendance records in bulk
    if new_attendances:
        Attendance.objects.bulk_create(new_attendances)
        print('All absent records created.')
    else:
        print('No employees to mark absent.')

# Home view using the simplified attendance fetch
def home(request):
    # Get the local timezone 'Asia/Kolkata'
    india_tz = pytz.timezone('Asia/Kolkata')
    
    # Ensure the current date and time are converted to local time
    today = localtime(timezone.now(), india_tz).date()
    current_time = localtime(timezone.now(), india_tz)

    # Define the late time threshold (11:30 AM) in the local time zone
    late_time_threshold = time(11, 30)  # This stays as-is because time() is timezone agnostic

    # Automatically mark all employees without attendance as absent
    employees_without_attendance = Employee.objects.exclude(attendance__date=today)
    Attendance.objects.bulk_create([
        Attendance(employee=employee, date=today, status='absent')
        for employee in employees_without_attendance
    ])

    # Fetch present employees
    present_today = Attendance.objects.filter(date=today, status='present')

    # Ensure the time comparison is done using local time
    late_today = Attendance.objects.filter(date=today, status='present', time__gt=late_time_threshold)
    on_time_today = Attendance.objects.filter(date=today, status='present', time__lte=late_time_threshold)

    # Treat employees without attendance records as absent
    absent_today = list(employees_without_attendance) + list(Attendance.objects.filter(date=today, status='absent'))

    context = {
        'present_today': present_today,
        'absent_today': absent_today,
        'late_today': late_today,
        'on_time_today': on_time_today,
    }

    return render(request, 'home.html', context)

# Other Views
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

# Key change: Simplify employee selection and attendance update
def select_employee(request):
    employees = Employee.objects.all()

    if request.method == "POST":
        form = EmployeeSelectionForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            attendance_status = form.cleaned_data['attendance_status']  # Should be 'present'
            today = timezone.now().date()
            current_time = timezone.now()

            # Update or create attendance record for the employee
            attendance, created = Attendance.objects.get_or_create(
                employee=employee, date=today,
                defaults={'status': 'absent', 'time': current_time}  # Defaults if record doesn't exist
            )

            # If the attendance record was created as absent, update it to the correct status
            if not created:
                attendance.status = attendance_status
                print(attendance.status)
                attendance.time = current_time
                attendance.save()

            messages.success(request, f"Attendance recorded for {employee}")
            return redirect('select_employee')
    else:
        form = EmployeeSelectionForm()

    return render(request, 'record_attendance.html', {'form': form, 'employees': employees})


# QR Code Generation
def dynamic_qr(request):
    todays_date = datetime.now().strftime('%d%m%y')
    domain = 'milankolkata.com'
    data = f"https://{domain}/user290901{todays_date}/"

    file_name = f'qrcode_{domain}_{todays_date}/.png'
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

@login_required
def employee_profile(request):
    employee = get_object_or_404(Employee, user=request.user)
    return render(request, 'employee_landing_pages/employee_profile.html', {'employee': employee})

@login_required
def employee_home(request):
    employee = get_object_or_404(Employee, user=request.user)
    return render(request, 'employee_landing_pages/employees_home.html', {'employee': employee})

@login_required
def employee_attendance_history(request):
    employee = request.user.employee

    month = request.GET.get('month')
    year = request.GET.get('year')

    if month and year:
        month = int(month)
        year = int(year)
    else:
        today = datetime.today()
        month = today.month
        year = today.year

    attendance_records = Attendance.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month
    ).order_by('-date')

    months = list(range(1, 13))
    all_years = Attendance.objects.filter(employee=employee).dates('date', 'year', order='DESC')
    years_list = [date.year for date in all_years] or [datetime.today().year]

    context = {
        'employee': employee,
        'attendance_records': attendance_records,
        'selected_month': month,
        'selected_year': year,
        'months': months,
        'years_list': years_list,
    }

    return render(request, 'employee_landing_pages/attendance_history.html', context)

def admin_attendance_history(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    month = request.GET.get('month')
    year = request.GET.get('year')

    if month and year:
        month = int(month)
        year = int(year)
    else:
        today = datetime.today()
        month = today.month
        year = today.year

    attendance_records = Attendance.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month
    ).order_by('-date')

    all_years = Attendance.objects.filter(employee=employee).dates('date', 'year', order='DESC')
    years_list = [date.year for date in all_years]

    months = list(range(1, 13))

    context = {
        'employee': employee,
        'attendance_records': attendance_records,
        'selected_month': month,
        'selected_year': year,
        'months': months,
        'years_list': years_list,
    }

    return render(request, 'admin_attendance_history.html', context)

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
