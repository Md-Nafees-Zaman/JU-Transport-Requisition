# transport/models.py
from django.db import models

class Transport(models.Model):
    VEHICLE_TYPES = [
        ('bus', 'Bus'),
        ('van', 'Van'),
        ('car', 'Car'),
        ('truck', 'Truck'),
        ('micro', 'Micro'),
    ]
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('maintenance', 'Maintenance'),
    ]

    vehicle_id = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    model = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=100, unique=True)
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES)
    driver = models.CharField(max_length=100)
    current_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.vehicle_id}"