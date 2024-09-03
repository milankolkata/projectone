from django.http import HttpResponse
from django.shortcuts import redirect

# def unauthenticated_user(view_func):
#     def wrapper_func(request, *args, **kwargs):
#         if request.user.is_authenticated:
#             print('decorator')
#             return redirect('home')
#         else:
#             return view_func(request *args, **kwargs)

#         return view_func(request, *args, **kwargs)
    
#     return wrapper_func



def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group_names = []
            if request.user.groups.exists():
                group_names = [group.name for group in request.user.groups.all()]  # Get list of group names
                print(group_names)  # Optional: For debugging

            # Check if any of the user's groups are in the allowed roles
            if any(group in allowed_roles for group in group_names):
                return view_func(request, *args, **kwargs)
            else:
                return redirect('home')

        return wrapper_func
    return decorator