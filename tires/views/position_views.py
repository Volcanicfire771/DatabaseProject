from django.shortcuts import render, get_object_or_404, redirect
from ..models import TirePosition
from ..forms.position_forms import TirePositionForm
from django.contrib import messages

def position_list(request):
    positions = TirePosition.objects.all().select_related('vehicle', 'mounted_tire').order_by('vehicle', 'tire_order')
    return render(request, 'tires/position_list.html', {
        'positions': positions,
        'form': TirePositionForm()
    })

def position_create(request):
    if request.method == "POST":
        form = TirePositionForm(request.POST)
        if form.is_valid():
            try:
                position = form.save()
                messages.success(request, f"Position '{position.position_name}' added to {position.vehicle}.")
            except Exception as e:
                messages.error(request, f"Database Error: {e}")
        else:
            messages.error(request, f"Error: {form.errors.as_text()}")
    return redirect('position_list')

def position_update(request, pk):
    position = get_object_or_404(TirePosition, pk=pk)
    if request.method == "POST":
        form = TirePositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            messages.success(request, "Position updated successfully.")
        else:
            messages.error(request, f"Update failed: {form.errors.as_text()}")
    return redirect('position_list')

def position_delete(request, pk):
    position = get_object_or_404(TirePosition, pk=pk)
    position.delete()
    messages.success(request, "Position removed.")
    return redirect('position_list')