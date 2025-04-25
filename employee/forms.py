# forms.py
from django import forms
from .models import TransportReservation

class TransportReservationForm(forms.ModelForm):
    class Meta:
        model = TransportReservation
        fields = ['reservation_date', 'from_time', 'to_time', 'destination', 'reservation_type', 'transport_type']
        widgets = {
            'reservation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'from_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'to_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'reservation_type': forms.Select(attrs={'class': 'form-select'}),
            'transport_type': forms.Select(attrs={'class': 'form-select'}),
        }
