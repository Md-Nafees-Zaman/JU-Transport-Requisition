from django.shortcuts import render, redirect
from .forms import TransportForm
from .models import Transport

def add_transport(request):
    if request.method == 'POST':
        form = TransportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # or any page you want to redirect to
    else:
        form = TransportForm()

    return render(request, 'transport/add_transport.html', {'form': form})

def transport_list(request):
    transports = Transport.objects.all()
    return render(request, 'transport/transport_list.html', {'transports': transports})