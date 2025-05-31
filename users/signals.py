from django.db.models.signals import post_save
from django.dispatch import receiver
from employee.models import TransportReservation
from .models import TransportPayment, LoginHistory
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.contrib.auth import get_user_model
User = get_user_model()

@receiver(post_save, sender=TransportReservation)
def create_transport_payment(sender, instance, created, **kwargs):
    if instance.approval_status == 'Approved' and not instance.payments.exists():
        # Calculate fee - you can customize this logic
        base_fee = 500  # Base fee
        if instance.transport_type == 'bus':
            base_fee = 1000
        elif instance.transport_type == 'car':
            base_fee = 800
            
        TransportPayment.objects.create(
            requisition=instance,
            amount=base_fee,
            status='pending'
        )

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    LoginHistory.objects.create(
        user=user,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        success=True
    )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    if user := User.objects.filter(email=credentials.get('username')).first():
        LoginHistory.objects.create(
            user=user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=False
        )