from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('adminn/', views.adminn, name='admin'),
    path('employee_details/', views.employee_details, name='employee_details'),
    path('employee_details/<int:pk>', views.individual_employee_details, name='individual_employee_details'),
    path('attendance/', views.select_employee, name='select_employee'),
    # path('home/home', views.home, name='home'),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout'),    
    path('add_employee', views.add_employee, name='add_employee'),
]
