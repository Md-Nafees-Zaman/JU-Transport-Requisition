from venv import logger
from django.db import models
from django.db.models import Q
from datetime import datetime, time

from employee.models import TransportReservation

from django.db import models
from django.db.models import Q
from datetime import datetime, time

# transport/models.py
class TransportQuerySet(models.QuerySet):
    def available_for_timeslot(self, date, from_time, to_time, transport_type=None):
        """
        Returns transports available for the given timeslot with optimized queries.
        """
        # Convert string inputs to proper types
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()
        
        if isinstance(from_time, str):
            from_time = time.fromisoformat(from_time)
        
        if isinstance(to_time, str):
            to_time = time.fromisoformat(to_time)

        # Create time range for the query
        time_range = (from_time, to_time)
        
        # Get conflicting transport IDs in a single query
        conflicting_transport_ids = (
            TransportReservation.objects
            .filter(
                reservation_date=date,
                transport__isnull=False
            )
            .filter(
                Q(from_time__lt=time_range[1]) & Q(to_time__gt=time_range[0])
            )
            .values_list('transport_id', flat=True)
            .distinct()
        )

        # Build the base queryset
        queryset = self.filter(availability_status='available')
        
        # Exclude conflicting transports if any exist
        if conflicting_transport_ids:
            queryset = queryset.exclude(id__in=conflicting_transport_ids)
            
        # Filter by transport type if specified
        if transport_type:
            queryset = queryset.filter(type=transport_type)

        return queryset.select_related('driver').only(
            'id',
            'vehicle_id',
            'type',
            'model',
            'registration_number',
            'driver__name',
            'availability_status'
        )


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

    objects = TransportQuerySet.as_manager()

    class Meta:
        ordering = ['vehicle_id']

    def __str__(self):
        return f"{self.get_type_display()} - {self.vehicle_id}"

    def is_available(self, date, from_time, to_time):
        """
        Check if this specific transport is available in the given time slot.
        """
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()
        if isinstance(from_time, str):
            from_time = time.fromisoformat(from_time)
        if isinstance(to_time, str):
            to_time = time.fromisoformat(to_time)

        return not TransportReservation.objects.filter(
            transport=self,
            reservation_date=date
        ).filter(
            Q(from_time__lt=to_time) & Q(to_time__gt=from_time)
        ).exists()
    

    @classmethod
    def get_availability_counts(cls, date, from_time, to_time):
        """
        Returns available vehicle counts by type for a given time slot
        """
        # Get approved reservations that conflict with this time slot
        conflicting_ids = TransportReservation.objects.filter(
            reservation_date=date,
            approval_status='Approved'
        ).filter(
            Q(from_time__lt=to_time) & Q(to_time__gt=from_time)
        ).values_list('transport_id', flat=True)

        # Get available vehicles not in conflicting reservations
        available = cls.objects.filter(
            availability_status='available'
        ).exclude(
            id__in=conflicting_ids
        )

        return {
            'bus': available.filter(type='bus').count(),
            'car': available.filter(type='car').count(),
            'micro': available.filter(type='micro').count(),
            'total': available.count()
        }
