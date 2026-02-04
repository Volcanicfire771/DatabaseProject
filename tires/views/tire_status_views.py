from django.shortcuts import render, get_object_or_404, redirect
from ..models import TireStatus
from ..forms.tire_status_forms import TireStatusForm
from django.contrib import messages

def tire_status_list(request):
    statuses = TireStatus.objects.all()
    return render(request, 'tires/tire_status_list.html', {
        'statuses': statuses,
        'form': TireStatusForm()
    })

def tire_status_create(request):
    if request.method == "POST":
        form = TireStatusForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New Tire Status created.")
        else:
            messages.error(request, f"Error: {form.errors.as_text()}")
    return redirect('tire_status_list')

def tire_status_update(request, pk):
    status = get_object_or_404(TireStatus, pk=pk)
    if request.method == "POST":
        form = TireStatusForm(request.POST, instance=status)
        if form.is_valid():
            form.save()
            messages.success(request, "Status updated successfully.")
    return redirect('tire_status_list')

def tire_status_delete(request, pk):
    status = get_object_or_404(TireStatus, pk=pk)
    status.delete()
    messages.success(request, "Status deleted.")
    return redirect('tire_status_list')