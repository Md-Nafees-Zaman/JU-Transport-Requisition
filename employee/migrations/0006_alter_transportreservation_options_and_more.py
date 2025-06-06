# Generated by Django 5.2 on 2025-05-29 07:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0005_alter_transportreservation_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transportreservation',
            options={},
        ),
        migrations.RemoveIndex(
            model_name='transportreservation',
            name='employee_tr_reserva_f00fd4_idx',
        ),
        migrations.RemoveIndex(
            model_name='transportreservation',
            name='employee_tr_transpo_2ad55f_idx',
        ),
        migrations.RemoveIndex(
            model_name='transportreservation',
            name='employee_tr_user_id_558726_idx',
        ),
        migrations.RemoveField(
            model_name='transportreservation',
            name='passengers',
        ),
        migrations.RemoveField(
            model_name='transportreservation',
            name='processed_by',
        ),
        migrations.RemoveField(
            model_name='transportreservation',
            name='purpose',
        ),
        migrations.RemoveField(
            model_name='transportreservation',
            name='updated_at',
        ),
        migrations.AlterField(
            model_name='transportreservation',
            name='approval_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='transportreservation',
            name='rejection_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transportreservation',
            name='reservation_type',
            field=models.CharField(choices=[('Official', 'Official'), ('Personal', 'Personal')], max_length=20),
        ),
        migrations.AlterField(
            model_name='transportreservation',
            name='transport_type',
            field=models.CharField(choices=[('micro', 'Micro'), ('bus', 'Bus'), ('car', 'Car')], max_length=20),
        ),
        migrations.AlterField(
            model_name='transportreservation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
