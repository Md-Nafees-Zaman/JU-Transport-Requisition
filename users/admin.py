from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User
from .forms import UserRegistrationForm

class CustomUserAdmin(UserAdmin):
    add_form = UserRegistrationForm
    form = UserRegistrationForm
    
    list_display = (
        'email', 'name', 'employee_ID',
        'department', 'designation', 'role', 'is_staff'
    )
    list_filter = ('role', 'department', 'is_staff', 'is_superuser')
    search_fields = ('email', 'name', 'employee_ID')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name', 'phone', 'address')}),
        (_('Professional Info'), {'fields': ('employee_ID', 'department', 'designation', 'role')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'phone',
                'address',
                'employee_ID',
                'department',
                'designation',
                'role'
            ),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_add_form = obj is None
        
        if not is_add_form:  # For change form
            form.base_fields.pop('password1', None)
            form.base_fields.pop('password2', None)
        
        if 'username' in form.base_fields:
            del form.base_fields['username']
            
        return form

admin.site.register(User, CustomUserAdmin)

from .models import Message

admin.site.register(Message)
