from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse
from .forms import UserRegistrationForm, UserUpdateForm, UserLoginForm

from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')  # Redirect to login after successful registration
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
        user = self.request.user
        role_redirects = {
            'employee': 'employee_dashboard',
            'registrar': 'registrar_dashboard',
            'transport': 'transport_dashboard',
            'bank': 'bank_dashboard'
        }
        return reverse(role_redirects.get(user.role, 'homepage'))

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

# Dashboard views remain the same
@login_required
def employee_dashboard(request):
    if request.user.role != 'employee':
        return redirect('homepage')
    return render(request, 'users/dashboards/employee_dashboard.html', {'user': request.user})

@login_required
def registrar_dashboard(request):
    if request.user.role != 'registrar':
        return redirect('homepage')
    return render(request, 'users/dashboards/registrar_dashboard.html', {'user': request.user})

@login_required
def transport_dashboard(request):
    if request.user.role != 'transport':
        return redirect('homepage')
    return render(request, 'users/dashboards/transport_dashboard.html', {'user': request.user})

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
    role = request.user.role
    return redirect(role_redirects.get(role, 'homepage'))

from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect

def logout_user(request):
    logout(request)
    messages.success(request, "")
    return redirect('homepage')  # Change 'homepage' to your actual homepage URL name if needed



# views.py
from django.shortcuts import render, redirect
from .forms import EmailSignupForm

def signup(request):
    if request.method == 'POST':
        form = EmailSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Add your post-registration logic here
            return redirect('verification_sent')
    else:
        form = EmailSignupForm()
    return render(request, 'users/signup.html', {'form': form})