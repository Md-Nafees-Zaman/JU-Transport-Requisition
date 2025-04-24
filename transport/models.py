from django.db import models

class Transport(models.Model):
    VEHICLE_TYPES = [
        ('bus', 'Bus'),
        ('van', 'Van'),
        ('car', 'Car'),
        ('truck', 'Truck'),
    ]
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('maintenance', 'Maintenance'),
    ]

    index = models.PositiveIntegerField()
    vehicle_id = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    model = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=100, unique=True)
    number_of_seats = models.PositiveIntegerField()
    rent_per_hour = models.DecimalField(max_digits=7, decimal_places=2)
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES)
    driver = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.type.capitalize()} - {self.vehicle_id}"
