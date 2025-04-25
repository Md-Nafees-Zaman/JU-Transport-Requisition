from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse
from .forms import (
    UserRegistrationForm, 
    UserUpdateForm, 
    UserLoginForm, 
    EmailSignupForm
)
from transport.models import Transport
from employee.models import TransportReservation

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

class CustomLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        role_redirects = {
            'employee': 'employee_dashboard',
            'registrar': 'registrar_dashboard',
            'transport': 'transport_dashboard',
            'bank': 'bank_dashboard'
        }
        return reverse(role_redirects.get(self.request.user.role, 'homepage'))

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})

def homepage(request):
    return render(request, 'users/homepage.html')

@login_required
def employee_dashboard(request):
    if request.user.role != 'employee':
        return redirect('homepage')
    
    requisitions = TransportReservation.objects.filter(user=request.user)
    
    context = {
        'user': request.user,
        'pending_requisitions': requisitions.filter(approval_status='Pending').count(),
        'approved_requests': requisitions.filter(approval_status='Approved').count(),
        'recent_requisitions': requisitions.order_by('-created_at')[:5],
        'transport_schedule': requisitions.filter(approval_status='Approved')[:3]
    }
    return render(request, 'users/dashboards/employee_dashboard.html', context)

@login_required
def transport_dashboard(request):
    if request.user.role != 'transport':
        return redirect('homepage')

    context = {
        'user': request.user,
        'applications': TransportReservation.objects.all().order_by('-reservation_date'),
        'ongoing_transports': TransportReservation.objects.filter(approval_status='Approved').count(),
        'available_vehicles': Transport.objects.filter(availability_status='available').count(),
        'active_transports': Transport.objects.filter(availability_status='available'),
        'map_center': '23.7806,90.2792'
    }
    return render(request, 'users/dashboards/transport_dashboard.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import User
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db import models
from .models import User  # Replace with get_user_model() if using a custom user model

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import render, redirect
from users.models import User
from transport.models import Transport

@login_required
def registrar_dashboard(request):
    if not request.user.role == 'registrar':
        return redirect('unauthorized')

    # User search and pagination
    query = request.GET.get('q')
    users = User.objects.all().order_by('-date_joined')

    if query:
        users = users.filter(
            models.Q(name__icontains=query) |
            models.Q(email__icontains=query) |
            models.Q(employee_ID__icontains=query)
        )

    paginator = Paginator(users, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Corrected transport counts using availability_status
    available_transports = Transport.objects.filter(availability_status='available').count()
    total_transports = Transport.objects.count()

    context = {
        'institution_name': "Jahangirnagar University",
        'academic_year': "2023/2024",
        'total_users': User.objects.count(),
        'all_users': User.objects.all().order_by('-date_joined'),
        'page_obj': page_obj,
        'available_transports': available_transports,
        'total_transports': total_transports,
    }

    return render(request, 'users/dashboards/registrar_dashboard.html', context)
@login_required
def bank_dashboard(request):
    if request.user.role != 'bank':
        return redirect('homepage')
    return render(request, 'users/dashboards/bank_dashboard.html', {'user': request.user})

@login_required
def dashboard_redirect(request):
    role_redirects = {
        'employee': 'employee_dashboard',
        'registrar': 'registrar_dashboard',
        'transport': 'transport_dashboard',
        'bank': 'bank_dashboard'
    }
    return redirect(role_redirects.get(request.user.role, 'homepage'))

def logout_user(request):
    logout(request)
    messages.success(request, "")
    return redirect('homepage')

def signup(request):
    if request.method == 'POST':
        form = EmailSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('verification_sent')
    else:
        form = EmailSignupForm()
    return render(request, 'users/signup.html', {'form': form})


# users/views.py
from django.views.generic import DetailView
from .models import User

class UserProfileView(DetailView):
    model = User
    template_name = 'users/user_profile.html'
    context_object_name = 'profile_user'