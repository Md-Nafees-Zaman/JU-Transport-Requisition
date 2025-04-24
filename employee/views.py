from django.shortcuts import render, redirect
from .forms import TransportReservationForm
from .models import TransportReservation
from django.contrib.auth.decorators import login_required

@login_required
def reserve_transport(request):
    if request.method == 'POST':
        form = TransportReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.save()
            return redirect('employee_dashboard')  # change to your actual dashboard name
    else:
        form = TransportReservationForm()
    return render(request, 'employee/reserve_transport.html', {'form': form})
