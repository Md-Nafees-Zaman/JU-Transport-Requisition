from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('registrar', 'Registrar'),
        ('transport', 'Transport Officer'),
        ('bank', 'Bank'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    name = models.CharField(max_length=255, default='Unnamed')
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    email = models.EmailField(unique=True)  # Keep unique email
    address = models.TextField()
    employee_ID = models.CharField(max_length=50, unique=True)

    # Keep username as USERNAME_FIELD for admin
    USERNAME_FIELD = 'username'  
    # Make email required
    REQUIRED_FIELDS = ['email']  

    def __str__(self):
        return f"{self.username} ({self.role})"
    




