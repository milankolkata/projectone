from django.shortcuts import render

# Create your views here.
#employee.home
def index(request):
    return render(request, 'index.html', {})