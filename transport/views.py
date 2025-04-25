# transport/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Transport
from employee.models import TransportReservation

def reservation_detail(request, reservation_id):
    reservation = get_object_or_404(TransportReservation, id=reservation_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            reservation.approval_status = 'Approved'
            reservation.rejection_reason = ''
        elif action == 'reject':
            reservation.approval_status = 'Rejected'
            reservation.rejection_reason = request.POST.get('rejection_reason', '')
        reservation.save()
        return redirect('transport_dashboard')
    
    return render(request, 'transport/reservation_detail.html', {'reservation': reservation})


from django.shortcuts import render, redirect
from .forms import TransportForm
from .models import Transport
from employee.models import TransportReservation

def add_transport(request):
    if request.method == 'POST':
        form = TransportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transport_list')
    else:
        form = TransportForm()
    return render(request, 'transport/add_transport.html', {'form': form})

def transport_list(request):
    transports = Transport.objects.all()
    return render(request, 'transport/transport_list.html', {'transports': transports})

def reservation_detail(request, reservation_id):
    reservation = TransportReservation.objects.get(id=reservation_id)
    
    if request.method == 'POST':
        if 'approve' in request.POST:
            reservation.approval_status = 'Approved'
        elif 'reject' in request.POST:
            reservation.approval_status = 'Rejected'
            reservation.rejection_reason = request.POST.get('rejection_reason', '')
        reservation.save()
        return redirect('transport_dashboard')
    
    return render(request, 'transport/reservation_detail.html', {'reservation': reservation})