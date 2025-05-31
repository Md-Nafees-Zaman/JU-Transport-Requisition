from django.db.models import Q
from datetime import datetime, time
from django.core.exceptions import ValidationError
import logging

from employee.models import TransportReservation

logger = logging.getLogger(__name__)

class AvailabilityService:
    @staticmethod
    def validate_timeslot(date_str, from_time_str, to_time_str):
        """Validate and convert time inputs"""
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            from_time = time.fromisoformat(from_time_str)
            to_time = time.fromisoformat(to_time_str)
            
            if from_time >= to_time:
                raise ValidationError("End time must be after start time")
                
            return date, from_time, to_time
        except ValueError as e:
            raise ValidationError(f"Invalid time format: {str(e)}")

    @staticmethod
    def get_available_transports(date_str, from_time_str, to_time_str, transport_type=None):
        """Get available transports with proper validation"""
        try:
            # Validate inputs
            date, from_time, to_time = AvailabilityService.validate_timeslot(
                date_str, from_time_str, to_time_str
            )
            
            # Find conflicting reservations
            conflicts = TransportReservation.objects.filter(
                reservation_date=date
            ).filter(
                Q(from_time__lt=to_time) & Q(to_time__gt=from_time)
            ).values_list('transport_id', flat=True)
            
            # Get available transports
            queryset = Transport.objects.exclude(id__in=conflicts)
            if transport_type:
                queryset = queryset.filter(transport_type=transport_type)
                
            return queryset
            
        except Exception as e:
            logger.error(f"Error in get_available_transports: {str(e)}")
            raise