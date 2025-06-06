# Generated by Django 5.2 on 2025-05-25 22:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0003_alter_transportreservation_transport_type'),
        ('users', '0002_alter_user_role_loginhistory_transportpayment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transportpayment',
            name='remarks',
        ),
        migrations.AlterField(
            model_name='transportpayment',
            name='processed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='transportpayment',
            name='requisition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='employee.transportreservation'),
        ),
        migrations.AlterField(
            model_name='transportpayment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending Approval'), ('approved', 'Approved'), ('paid', 'Paid'), ('rejected', 'Rejected')], default='pending', max_length=20),
        ),
    ]
