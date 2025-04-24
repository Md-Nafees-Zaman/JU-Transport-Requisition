from django import forms
from .models import Transport

class TransportForm(forms.ModelForm):
    class Meta:
        model = Transport
        fields = '__all__'
        widgets = {
            'availability_status': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
        }
