from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.utils import timezone


# ==========================
# Custom User Manager
# ==========================
class CustomUserManager(BaseUserManager):
    def create_inactive_user(self, email, **extra_fields):
        """Create unverified user for registrar-created accounts"""
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_verified', False)
        return self._create_user(email, None, **extra_fields)

    def create_user(self, email, password=None, **extra_fields):
        """Create standard verified user"""
        extra_fields.setdefault('is_verified', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create admin user with full privileges"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', 'registrar')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def _create_user(self, email, password, **extra_fields):
        """Base user creation logic"""
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user


# ==========================
# Custom User Model
# ==========================
class User(AbstractUser):
    # Disable username field
    username = None

    # Replace with email-based login
    email = models.EmailField(_('email address'), unique=True)
    is_verified = models.BooleanField(_('verified'), default=False)

    # Extra user fields
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('registrar', 'Registrar'),
        ('transport', 'Transport Officer'),
        ('bank', 'Bank'),
    ]
    role = models.CharField(_('role'), max_length=20, choices=ROLE_CHOICES)
    name = models.CharField(_('full name'), max_length=255)
    phone = models.CharField(_('phone number'), max_length=15)
    department = models.CharField(_('department'), max_length=100)
    designation = models.CharField(_('designation'), max_length=100)
    address = models.TextField(_('address'))
    employee_ID = models.CharField(_('employee ID'), max_length=50, unique=True)

    # Configuration
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def send_activation_email(self):
        """Send account activation email with password setup link"""
        subject = "Activate Your Account"
        context = {
            'user': self,
            'uid': urlsafe_base64_encode(force_bytes(self.pk)),
            'token': default_token_generator.make_token(self),
            'protocol': 'https' if settings.SECURE_SSL_REDIRECT else 'http',
            'domain': settings.DOMAIN,
        }

        send_mail(
            subject,
            render_to_string('users/activation_email.txt', context),
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            html_message=render_to_string('users/activation_email.html', context),
            fail_silently=False
        )

    @property
    def is_bank_staff(self):
        return self.role == 'bank'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


# ==========================
# Transport Payment Model
# ==========================
class TransportPayment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected')
    ]

    requisition = models.ForeignKey(
        'employee.TransportReservation',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transport Payment'
        verbose_name_plural = 'Transport Payments'

    def __str__(self):
        return f"Payment #{self.id} - {self.requisition.user.name} (৳{self.amount})"

    @property
    def status_badge(self):
        status_colors = {
            'pending': 'warning',
            'approved': 'success',
            'paid': 'info',
            'rejected': 'danger'
        }
        return status_colors.get(self.status, 'secondary')

    @property
    def formatted_amount(self):
        return f"৳{self.amount:,.2f}"


# ==========================
# Login History Model
# ==========================
class LoginHistory(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_history'
    )
    ip_address = models.CharField(max_length=45)
    user_agent = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    success = models.BooleanField(default=True)
    location = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name_plural = 'Login Histories'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.email} - {self.timestamp}"

    def get_status_icon(self):
        return 'check-circle-fill' if self.success else 'x-circle-fill'


from django.db import models
from django.utils import timezone

class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)  # Add this field
    is_read = models.BooleanField(default=False)  # Optional: for tracking read status

    def __str__(self):
        return f"{self.subject} - {self.name}"
