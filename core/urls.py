from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('employee_details/', views.employee_details, name='employee_details'),
    path('employee_details/<int:pk>/', views.individual_employee_details, name='individual_employee_details'),
    path('attendance_manual/', views.select_employee, name='select_employee'),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),    
    path('add_employee/', views.add_employee, name='add_employee'),
    
    # Updated URLs for the four use cases with a unified view function
    path('attendance/present/', views.attendance_status_view, {'status_type': 'present'}, name='today_present'),
    path('attendance/absent/', views.attendance_status_view, {'status_type': 'absent'}, name='today_absent'),
    path('attendance/late/', views.attendance_status_view, {'status_type': 'late'}, name='today_late'),
    path('attendance/on_time/', views.attendance_status_view, {'status_type': 'on_time'}, name='today_on_time'),


    path('attendance_qr/', views.dynamic_qr, name='attendance_qr'),

    # Employees landing pages
    path('profile/', views.employee_profile, name='profile'),
    path('e_home/', views.employee_home, name='employee_home'),
    path('attendance_history/', views.employee_attendance_history, name='employee_attendance_history'),
    path('attendance-history/<int:employee_id>/', views.admin_attendance_history, name='admin_attendance_history'),

    # URL pattern for user attendance with the static part '290901' and a dynamic date string
    path('user290901<str:date_str>/', views.user_attendance, name='user_attendance'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
