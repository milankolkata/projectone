from django.urls import path
from . import views
from datetime import datetime
from django.conf import settings
from django.conf.urls.static import static


random_number = '290901'

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('adminn/', views.adminn, name='admin'),
    path('employee_details/', views.employee_details, name='employee_details'),
    path('employee_details/<int:pk>/', views.individual_employee_details, name='individual_employee_details'),
    path('attendance_manual/', views.select_employee, name='select_employee'),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout'),    
    path('add_employee/', views.add_employee, name='add_employee'),
    path('today_present/', views.today_present, name='today_present'),
    path('today_absent/', views.today_absent, name='today_absent'),
    path('today_late/', views.today_late, name='today_late'),
    path('today_on_time/', views.today_on_time, name='today_on_time'),
    path('attendance_qr/', views.dynamic_qr, name='attendance_qr'),
    
    # Use lambda to ensure that today's date is fetched at runtime
    path(f'user{random_number}<slug:date>', views.user_attendance, name='user_attendance'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
