# employee/views.py
from django.shortcuts import render, redirect
from .forms import TransportReservationForm
from .models import TransportReservation
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
@login_required
def reserve_transport(request):
    if request.method == 'POST':
        form = TransportReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.save()
            return redirect('employee_dashboard')
    else:
        form = TransportReservationForm()
    return render(request, 'employee/reserve_transport.html', {'form': form})

@login_required
def my_requisitions(request):
    requisitions = TransportReservation.objects.filter(user=request.user)
    
    context = {
        'pending_requisitions': requisitions.filter(approval_status='Pending'),
        'approved_requisitions': requisitions.filter(approval_status='Approved'),
        'rejected_requisitions': requisitions.filter(approval_status='Rejected'),
    }
    return render(request, 'employee/my_requisitions.html', context)


# employee/views.py
@login_required
def requisition_detail(request, pk):
    requisition = get_object_or_404(
        TransportReservation, 
        id=pk,
        user=request.user  # Ensure users can only view their own requisitions
    )
    return render(request, 'employee/requisition_detail.html', {
        'requisition': requisition
    })