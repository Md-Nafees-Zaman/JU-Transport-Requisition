# Generated by Django 5.2 on 2025-05-28 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0003_alter_transport_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transport',
            options={'ordering': ['type', 'vehicle_id'], 'verbose_name': 'Transport Vehicle', 'verbose_name_plural': 'Transport Vehicles'},
        ),
        migrations.AddField(
            model_name='transport',
            name='capacity',
            field=models.PositiveIntegerField(default=4),
        ),
        migrations.AddField(
            model_name='transport',
            name='current_location',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='transport',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='transport',
            name='availability_status',
            field=models.CharField(choices=[('available', 'Available'), ('booked', 'Booked'), ('maintenance', 'Under Maintenance'), ('out_of_service', 'Out of Service')], default='available', max_length=20),
        ),
        migrations.AlterField(
            model_name='transport',
            name='driver',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='transport',
            name='type',
            field=models.CharField(choices=[('bus', 'Bus'), ('car', 'Car'), ('van', 'Van'), ('micro', 'Microbus'), ('truck', 'Truck')], max_length=20),
        ),
    ]
