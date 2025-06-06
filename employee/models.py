# employee/models.py
from django.db import models
from django.conf import settings

class TransportReservation(models.Model):
    TRANSPORT_TYPES = [
        ('micro', 'Micro'),
        ('bus', 'Bus'),
        ('car', 'Car'),
    ]
    RESERVATION_TYPES = [
        ('Official', 'Official'),
        ('Personal', 'Personal'),
    ]
    APPROVAL_STATUS = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reservation_date = models.DateField()
    from_time = models.TimeField()
    to_time = models.TimeField()
    destination = models.CharField(max_length=255)
    reservation_type = models.CharField(max_length=20, choices=RESERVATION_TYPES)
    transport_type = models.CharField(max_length=20, choices=TRANSPORT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    approval_status = models.CharField(max_length=10, choices=APPROVAL_STATUS, default='Pending')
    rejection_reason = models.TextField(null=True, blank=True)
    transport = models.ForeignKey(
        'transport.Transport', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations'
    )

    def __str__(self):
        return f"{self.user.username} - {self.reservation_date} ({self.transport_type})"

    @property
    def status_badge(self):
        return {
            'Pending': 'warning',
            'Approved': 'success',
            'Rejected': 'danger'
        }.get(self.approval_status, 'secondary')


from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

    class Meta:
        ordering = ['-created_at']