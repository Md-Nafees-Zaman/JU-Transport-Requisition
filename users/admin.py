from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import UserRegistrationForm

class CustomUserAdmin(UserAdmin):
    # Use your custom form for adding/changing users
    add_form = UserRegistrationForm
    form = UserRegistrationForm
    
    # Admin list view configuration
    list_display = (
        'username', 'email', 'name', 'employee_ID',
        'department', 'designation', 'role', 'is_staff'
    )
    list_filter = ('role', 'department', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'name', 'employee_ID')
    ordering = ('username',)
    
    # Fieldsets for edit page
    fieldsets = (
        (None, {'fields': ('username', 'password')}),  # Keep username for admin
        ('Personal Info', {'fields': (
            'name', 'email', 'phone', 'address'
        )}),
        ('Professional Info', {'fields': (
            'employee_ID', 'department', 'designation', 'role'
        )}),
        ('Permissions', {'fields': (
            'is_active', 'is_staff', 'is_superuser',
            'groups', 'user_permissions'
        )}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Fieldsets for add page (matches your registration form)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email',  # Both required
                'password1', 'password2',
                'name', 'phone', 'address',
                'employee_ID', 'department',
                'designation', 'role'
            ),
        }),
    )
    
    # Customize the form to handle email as username for frontend
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # If this is the frontend login form, modify it
        if not request.user.is_staff and 'username' in form.base_fields:
            form.base_fields['username'].label = 'Email'
        return form

admin.site.register(User, CustomUserAdmin)