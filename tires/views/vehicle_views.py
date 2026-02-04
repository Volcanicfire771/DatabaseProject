from django.shortcuts import render, get_object_or_404, redirect
from ..models import WorkOrder, Vehicle, Employee
from django.contrib import messages
from ..forms.vehicle_forms import VehicleForm 

def vehicle_list(request):
    vehicles = Vehicle.objects.all()
    context = {
        'vehicles': vehicles,
        'create_form': VehicleForm(),
    }
    return render(request, 'tires/vehicle_list.html', context)

def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    vehicle.delete()  # FIX: Use lowercase 'vehicle' (the instance), not 'Vehicle' (the class)
    messages.success(request, "Vehicle deleted.")
    return redirect('vehicle_list')

def vehicle_create(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, f"Vehicle {vehicle.license_plate} created.")
        else:
            # Better error message to see what went wrong
            messages.error(request, f"Error: {form.errors}")
    
    return redirect('vehicle_list')

def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    
    if request.method == "POST":
        form = VehicleForm(request.POST, instance=vehicle)
        
        if form.is_valid():
            form.save()
            messages.success(request, f"Vehicle {vehicle.license_plate} updated successfully.")
        else:
            error_msg = "Update failed: " + ", ".join([f"{k}: {v[0]}" for k, v in form.errors.items()])
            messages.error(request, error_msg)
            
    return redirect('vehicle_list')