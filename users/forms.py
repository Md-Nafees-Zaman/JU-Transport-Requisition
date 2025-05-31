from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordResetForm,AuthenticationForm  
from .models import User
from transport.models import Transport

class UserRegistrationForm(forms.ModelForm):
    """
    Registrar's form for creating new users without passwords
    """
    class Meta:
        model = User
        fields = [
            'email', 'name', 'phone', 'department',
            'designation', 'address', 'employee_ID', 'role'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'autocomplete': 'off'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()  # No password yet
        user.is_active = False  # Requires activation
        user.username = user.email  # Set username = email
        if commit:
            user.save()
        return user

class ActivationForm(forms.Form):
    """
    Form for employees to initiate the activation process
    """
    email = forms.EmailField(
        label='Registered Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your institutional email',
            'autocomplete': 'email'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if not User.objects.filter(email=email, is_active=False).exists():
            raise ValidationError(
                "This email is either already active or not registered."
            )
        return email

class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom password reset form for activation process
    """
    def get_users(self, email):
        """Get inactive users matching email (case-insensitive)"""
        return User.objects.filter(
            email__iexact=email,
            is_active=False
        )

    def save(self, **kwargs):
        """Override to prevent active users from receiving reset emails"""
        kwargs['domain_override'] = True
        return super().save(**kwargs)
    

# Add UserLoginForm
class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'department', 'designation', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class RejectionForm(forms.Form):
    remarks = forms.CharField(
        label="Reason for Rejection",
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Provide a clear reason for rejecting this payment...'
        }),
        required=True
    )



from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import time

class AvailabilityCheckForm(forms.Form):
    reservation_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now
    )
    from_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        initial=time(8, 0)
    )
    to_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        initial=time(17, 0)
    )
    transport_type = forms.ChoiceField(
        choices=Transport.VEHICLE_TYPES,
        required=False,
        label="Filter by Vehicle Type"
    )

    def clean(self):
        cleaned_data = super().clean()
        from_time = cleaned_data.get('from_time')
        to_time = cleaned_data.get('to_time')
        
        if from_time and to_time and from_time >= to_time:
            raise ValidationError("End time must be after start time")
        
        return cleaned_data