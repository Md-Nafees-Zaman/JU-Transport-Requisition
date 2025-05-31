from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordResetConfirmView
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import DetailView
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .forms import RejectionForm, UserUpdateForm
from django.utils import timezone
from django.db.models import Max
from django.contrib import messages as django_messages

from .forms import (
    UserRegistrationForm,
    UserUpdateForm,
    UserLoginForm,
    ActivationForm,
    CustomPasswordResetForm
)
from .models import User
from transport.models import Transport
from employee.models import TransportReservation

def register(request):
    """Registrar's view to create new users without passwords"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"User {user.email} registered successfully. "
                "They must activate their account via email."
            )
            return redirect('registrar_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

class CustomLoginView(LoginView):
    """Custom login view with role-based redirection"""
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
    """User profile update view"""
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
    """Application homepage"""
    return render(request, 'users/homepage.html')

# Dashboard Views
@login_required
def employee_dashboard(request):
    """Employee-specific dashboard"""
    if request.user.role != 'employee' or not request.user.is_active:
        return redirect('homepage')
    
    requisitions = TransportReservation.objects.filter(user=request.user)
    
    context = {
        'pending_requisitions': requisitions.filter(approval_status='Pending').count(),
        'approved_requests': requisitions.filter(approval_status='Approved').count(),
        'recent_requisitions': requisitions.order_by('-created_at')[:5],
        'transport_schedule': requisitions.filter(approval_status='Approved')[:3]
    }
    return render(request, 'users/dashboards/employee_dashboard.html', context)

from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.utils import timezone
from employee.models import TransportReservation,Message
from transport.models import Transport


@login_required
def transport_dashboard(request):
    """Transport officer dashboard with premium pagination"""
    if request.user.role != 'transport':
        return redirect('homepage')

    today = timezone.now().date()

    # Paginate applications
    applications_list = TransportReservation.objects.all().order_by('-reservation_date')
    paginator_applications = Paginator(applications_list, 10)  # Show 10 applications per page
    page_number_applications = request.GET.get('page_applications', 1)
    applications = paginator_applications.get_page(page_number_applications)

    # Paginate messages
    messages_list = Message.objects.all().order_by('-created_at')
    paginator_messages = Paginator(messages_list, 10)  # Show 10 messages per page
    page_number_messages = request.GET.get('page_messages', 1)
    message_list = paginator_messages.get_page(page_number_messages)

    context = {
        'applications': applications,
        'ongoing_transports': TransportReservation.objects.filter(
            approval_status='Approved',
            reservation_date=today
        ).count(),
        'available_vehicles': Transport.objects.filter(availability_status='available').count(),
        'active_transports': Transport.objects.filter(availability_status='available'),
        'message_list': message_list,
        'django_messages': django_messages.get_messages(request),
    }
    return render(request, 'users/dashboards/transport_dashboard.html', context)
@login_required
def registrar_dashboard(request):
    if request.user.role != 'registrar':
        return redirect('unauthorized')

    # User management
    users = User.objects.all().order_by('-date_joined')
    query = request.GET.get('q')
    
    if query:
        users = users.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(employee_ID__icontains=query)
        )

    paginator = Paginator(users, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'pending_activation': User.objects.filter(is_active=False).count(),
        'available_transports': Transport.objects.filter(availability_status='available').count(),
        'total_transports': Transport.objects.count(),
        'institution_name': "Jahangirnagar University",
        'academic_year': "2023/2024",
        'available_vehicles': Transport.objects.filter(availability_status='available').count(),

    }
    return render(request, 'users/dashboards/registrar_dashboard.html', context)

from django.db.models import Sum, Count, Q
from .models import TransportPayment, LoginHistory
from employee.models import TransportReservation
@login_required
def bank_dashboard(request):
    if request.user.role != 'bank':
        return redirect('unauthorized')

    # Payment statistics with proper aggregation
    payment_stats = TransportPayment.objects.aggregate(
        total_pending=Sum('amount', filter=Q(status='pending')),
        total_approved=Sum('amount', filter=Q(status='approved')),
        total_paid=Sum('amount', filter=Q(status='paid')),
        pending_count=Count('id', filter=Q(status='pending')),
        approved_count=Count('id', filter=Q(status='approved')),
        paid_count=Count('id', filter=Q(status='paid'))
    )

    # Employee-wise payment summary
    employee_payments = TransportPayment.objects.values(
        'requisition__user__employee_ID',
        'requisition__user__name',
        'requisition__user__department'
    ).annotate(
        pending=Sum('amount', filter=Q(status='pending')),
        approved=Sum('amount', filter=Q(status='approved')),
        paid=Sum('amount', filter=Q(status='paid')),
        total=Sum('amount'),
        last_transaction=Max('processed_at')
    ).order_by('-total')

    # Chart data - last 30 days
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    chart_data = TransportPayment.objects.filter(
        processed_at__gte=thirty_days_ago
    ).extra({
        'date': "date(processed_at)"
    }).values('date').annotate(
        pending=Sum('amount', filter=Q(status='pending')),
        approved=Sum('amount', filter=Q(status='approved'))
    ).order_by('date')

    context = {
        'financial_summary': {
            'pending': payment_stats['total_pending'] or 0,
            'approved': payment_stats['total_approved'] or 0,
            'paid': payment_stats['total_paid'] or 0,
            'all': (payment_stats['total_pending'] or 0) + 
                   (payment_stats['total_approved'] or 0) + 
                   (payment_stats['total_paid'] or 0),
            'pending_count': payment_stats['pending_count'],
            'approved_count': payment_stats['approved_count'],
            'paid_count': payment_stats['paid_count']
        },
        'employee_payments': employee_payments,
        'chart_data': {
            'dates': [item['date'].strftime("%Y-%m-%d") for item in chart_data],
            'pending': [float(item['pending'] or 0) for item in chart_data],
            'approved': [float(item['approved'] or 0) for item in chart_data]
        }
    }
    return render(request, 'users/dashboards/bank_dashboard.html', context)
@login_required
def dashboard_redirect(request):
    """Redirect users to their appropriate dashboard"""
    role_redirects = {
        'employee': 'employee_dashboard',
        'registrar': 'registrar_dashboard',
        'transport': 'transport_dashboard',
        'bank': 'bank_dashboard'
    }
    return redirect(role_redirects.get(request.user.role, 'homepage'))

def logout_user(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, "")
    return redirect('homepage')

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

def signup(request):
    """Handle email verification requests"""
    if request.method == 'POST':
        form = ActivationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            
            # Generate verification email
            subject = "Complete Your Account Activation"
            context = {
                'user': user,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http',
                'domain': request.get_host(),
            }
            
            # Send activation email
            send_mail(
                subject,
                render_to_string('users/activation_email.txt', context),
                'noreply@juniv.edu',
                [email],
                html_message=render_to_string('users/activation_email.html', context),
                fail_silently=False
            )
            return redirect('activation_sent')
    else:
        form = ActivationForm()
    
    return render(request, 'users/signup.html', {'form': form})

from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.forms import SetPasswordForm

class ActivationConfirmView(PasswordResetConfirmView):
    """Handle account activation through password reset confirmation"""
    template_name = 'users/activation_confirm.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('login')  # Redirect to login page after activation

    def form_valid(self, form):
        # Save password using parent's logic
        response = super().form_valid(form)
        
        # Get validated user from the view
        user = self.user
        
        # Activate and verify user
        user.is_active = True
        user.is_verified = True
        user.save(update_fields=['is_active', 'is_verified'])
        
        # Add success message that will persist through redirect
        messages.success(
            self.request,
            'Account successfully activated! Please log in with your new password.'
        )
        
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_activation'] = True
        return context


# forms.py
from django.contrib.auth.forms import SetPasswordForm

class CustomPasswordResetForm(SetPasswordForm):
    # Custom styling or additional validation if needed
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class UserProfileView(DetailView):
    """Public user profile view"""
    model = User
    template_name = 'users/user_profile.html'
    context_object_name = 'profile_user'
    slug_field = 'pk'
    slug_url_kwarg = 'pk'

def activation_sent(request):
    """Confirmation page after activation email sent"""
    return render(request, 'users/activation_sent.html')

def unauthorized(request):
    """Unauthorized access view"""
    return render(request, 'users/unauthorized.html', status=403)


from django.contrib.auth import views as auth_views

# Separate view for regular password resets
class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')



@login_required
def payment_detail(request, pk):
    payment = get_object_or_404(TransportPayment, pk=pk)
    return render(request, 'bank/payment_detail.html', {'payment': payment})

@login_required
def approve_payment(request, pk):
    payment = get_object_or_404(TransportPayment, pk=pk)
    if request.method == 'POST':
        payment.status = 'approved'
        payment.processed_by = request.user
        payment.processed_at = timezone.now()
        payment.save()
        
        messages.success(request, f"Payment #{payment.id} approved successfully.")
        return redirect('bank_dashboard')
    
    return render(request, 'bank/confirm_approval.html', {'payment': payment})

@login_required
def reject_payment(request, pk):
    payment = get_object_or_404(TransportPayment, pk=pk)
    if request.method == 'POST':
        form = RejectionForm(request.POST)
        if form.is_valid():
            payment.status = 'rejected'
            payment.processed_by = request.user
            payment.processed_at = timezone.now()
            payment.remarks = form.cleaned_data['remarks']
            payment.save()
            
            messages.warning(request, f"Payment #{payment.id} has been rejected.")
            return redirect('bank_dashboard')
    else:
        form = RejectionForm()
    
    return render(request, 'bank/reject_payment.html', {
        'payment': payment,
        'form': form
    })


from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Q

def export_payments(request):
    """Export payments to PDF"""
    if request.user.role != 'bank':
        return redirect('unauthorized')

    payments = TransportPayment.objects.filter(
        Q(status='approved') | Q(status='paid')
    ).order_by('-processed_at')

    html_string = render_to_string(
        'users/payments_pdf.html',
        {'payments': payments}
    )

    html = HTML(string=html_string)
    result = html.write_pdf()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transport_payments.pdf"'
    response.write(result)

    return response



@login_required
def approve_reservation(request, pk):
    if request.user.role not in ['registrar', 'transport']:
        return redirect('unauthorized')
        
    reservation = get_object_or_404(TransportReservation, pk=pk)
    
    if request.method == 'POST':
        reservation.approval_status = 'Approved'
        reservation.save()  # This will trigger the signal
        
        messages.success(request, 
            f"Reservation #{reservation.id} approved successfully. "
            "Payment request has been generated."
        )
        return redirect('transport_dashboard')
    
    return render(request, 'users/approve_reservation.html', {
        'reservation': reservation
    })


# transport/views.py
from django.shortcuts import render
from datetime import time

def pricing(request):
    # Define pricing structure
    vehicle_types = {
        'bus': {
            'name': 'University Bus',
            'base_fare': 500,
            'per_km': 20,
            'capacity': '30-40 people',
            'icon': 'bi-bus-front'
        },
        'microbus': {
            'name': 'Microbus',
            'base_fare': 800,
            'per_km': 30,
            'capacity': '12-15 people',
            'icon': 'bi-truck'
        },
        'car': {
            'name': 'Sedan Car',
            'base_fare': 1000,
            'per_km': 40,
            'capacity': '4 people',
            'icon': 'bi-car-front'
        },
        'ambulance': {
            'name': 'Ambulance',
            'base_fare': 1500,
            'per_km': 50,
            'capacity': 'Patient + 2 attendants',
            'icon': 'bi-truck-front'         }
    }
    
    # Time-based multipliers
    time_slots = {
        'normal': {'name': 'Regular Hours (8AM-6PM)', 'multiplier': 1.0},
        'peak': {'name': 'Peak Hours (7-8AM, 6-8PM)', 'multiplier': 1.2},
        'late_night': {'name': 'Late Night (8PM-12AM)', 'multiplier': 1.5},
        'emergency': {'name': 'Emergency (12AM-7AM)', 'multiplier': 2.0}
    }
    
    # Additional services
    additional_services = [
        {'name': 'Driver Allowance (per hour)', 'price': 200},
        {'name': 'AC Service', 'price': 300},
        {'name': 'Priority Booking', 'price': 500},
        {'name': 'Round Trip', 'price': '1.5x one-way'},
        {'name': 'Waiting Time (per 30min)', 'price': 200}
    ]
    
    context = {
        'title': 'Pricing - JU Transport System',
        'vehicle_types': vehicle_types,
        'time_slots': time_slots,
        'additional_services': additional_services,
        'sample_calculations': [
            {
                'description': 'Bus trip to Dhaka (20km) during peak hours',
                'calculation': '500 (base) + (20km × 20) + 20% peak charge = 500 + 400 + 180 = 1080 BDT'
            },
            {
                'description': 'Car trip inside campus during regular hours',
                'calculation': '1000 (base) = 1000 BDT'
            },
            {
                'description': 'Emergency ambulance at night (10km)',
                'calculation': '1500 (base) + (10km × 50) + 100% emergency charge = 1500 + 500 + 2000 = 4000 BDT'
            }
        ]
    }
    return render(request, 'users/pricing.html', context)

def contact(request):
    context = {
        'title': 'Contact Us - JU Transport System',
        'departments': [
            {
                'name': 'Support',
                'email': 'support@jutransport.edu.bd',
                'phone': '+880 1234 567890',
                'hours': '8:00 AM - 5:00 PM (Sat-Thu)'
            },
            {
                'name': 'Administration',
                'email': 'admin@jutransport.edu.bd',
                'phone': '+880 1234 567891',
                'hours': '9:00 AM - 4:00 PM (Sat-Thu)'
            },
            {
                'name': 'Technical Issues',
                'email': 'tech@jutransport.edu.bd',
                'phone': '+880 1234 567892',
                'hours': '10:00 AM - 6:00 PM (Sat-Thu)'
            }
        ],
        'location': {
            'address': 'Transport Office, Jahangirnagar University, Savar, Dhaka-1342, Bangladesh',
            'map_url': 'https://maps.google.com/?q=Jahangirnagar+University'
        }
    }
    return render(request, 'users/contact.html', context)




from django.core.mail import send_mail
from django.conf import settings
from .models import Message

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')

        if not all([name, email, subject, message_text]):
            return render(request, 'users/contact.html', {
                'error': 'All fields are required.'
            })

        # Save message to DB
        try:
            message = Message.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_text
            )
            
            # Send email to admin
            send_mail(
                f"Transport Message: {subject}",
                f"From: {name} <{email}>\n\n{message_text}\n\n---\n"
                f"Reply URL: {request.build_absolute_uri(f'/transport/messages/{message.id}/reply/')}",
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            
            return render(request, 'users/contact.html', {
                'success': 'Message sent successfully!'
            })
            
        except Exception as e:
            return render(request, 'users/contact.html', {
                'error': f'Failed to send message: {str(e)}'
            })

    return render(request, 'users/contact.html')

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def message_list(request):
    all_messages = Message.objects.all().order_by('-created_at')
    return render(request, 'users/messages.html', {'messages': all_messages})

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Message

@login_required
@require_POST
def message_delete(request, message_id):
    try:
        # Get message and verify ownership or permissions
        msg = Message.objects.get(id=message_id)
        
        # Add any additional permission checks here if needed
        # Example: if not request.user.is_staff and msg.user != request.user:
        #     return JsonResponse({'status': 'error', 'message': 'Not authorized'}, status=403)
        
        msg.delete()
        return JsonResponse({'status': 'success', 'message': 'Message deleted'})
    
    except Message.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Message not found'}, status=404)
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    

from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import logging
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from datetime import datetime, time

logger = logging.getLogger(__name__)
@require_POST
def check_availability(request):
    """Handle vehicle availability check with type counts"""
    try:
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'AJAX required'}, status=400)

        try:
            data = json.loads(request.body)
            date = datetime.strptime(data['reservation_date'], '%Y-%m-%d').date()
            from_time = time.fromisoformat(data['from_time'])
            to_time = time.fromisoformat(data['to_time'])
            
            if from_time >= to_time:
                raise ValidationError("End time must be after start time")

            # Get total counts of each vehicle type
            vehicle_counts = {
                'bus': Transport.objects.filter(type='bus', availability_status='available').count(),
                'car': Transport.objects.filter(type='car', availability_status='available').count(),
                'micro': Transport.objects.filter(type='micro', availability_status='available').count()
            }

            # Get conflicting transport IDs for the time slot
            conflicting_ids = TransportReservation.objects.filter(
                reservation_date=date,
                approval_status='Approved'  # Only count approved reservations
            ).filter(
                Q(from_time__lt=to_time) & Q(to_time__gt=from_time)
            ).values_list('transport_id', flat=True)

            # Get available counts by type
            available_query = Transport.objects.filter(
                availability_status='available'
            ).exclude(
                id__in=conflicting_ids
            )

            availability_summary = {
                'bus': available_query.filter(type='bus').count(),
                'car': available_query.filter(type='car').count(),
                'micro': available_query.filter(type='micro').count()
            }

            context = {
                'reservation_date': data['reservation_date'],
                'from_time': data['from_time'],
                'to_time': data['to_time'],
                'transport_type': data.get('transport_type'),
                'availability_summary': availability_summary,
                'vehicle_counts': vehicle_counts
            }

            return JsonResponse({
                'status': 'success',
                'html': render_to_string('users/_availability_results.html', context)
            })

        except (json.JSONDecodeError, ValueError, ValidationError) as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Availability check error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Server error'}, status=500)

    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'System error'}, status=500)
    


from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@login_required
@user_passes_test(lambda u: u.role == 'registrar', login_url='homepage')
def delete_user(request, user_id):
    if request.method == 'POST':
        user_to_delete = get_object_or_404(User, id=user_id)
        
        # Prevent self-deletion and deletion of other registrars
        if user_to_delete == request.user:
            messages.error(request, "You cannot delete your own account!")
        elif user_to_delete.role == 'registrar' and not request.user.is_superuser:
            messages.error(request, "Only superusers can delete registrar accounts!")
        else:
            user_to_delete.delete()
            messages.success(request, f"User {user_to_delete.name} has been deleted successfully")
        
        return redirect('registrar_dashboard')
    
    # If not POST, redirect to dashboard
    return redirect('registrar_dashboard')