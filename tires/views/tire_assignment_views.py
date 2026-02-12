from django.shortcuts import render, redirect, get_object_or_404 
from ..models import TirePosition, Tire, TireAssignment, WorkOrder, Vehicle
from django.contrib import messages
from django.http import HttpResponse

# 1. THE MAIN LIST
def assignment_list(request):
    assignments = TireAssignment.objects.all().order_by('-assignment_date')
    vehicles_with_open_wo = Vehicle.objects.filter(workorder__status='O').distinct()
    context = {
        'assignments': assignments,
        'tires': Tire.objects.all(),
        'positions': TirePosition.objects.filter(mounted_tire__isnull=True),
        'vehicles_with_open_wo': vehicles_with_open_wo,        
        'work_orders': WorkOrder.objects.filter(status='O'), # Fixed status code
    }
    return render(request, 'tires/assignment_list.html', context)

# 2. THE TIRE HISTORY (Individual tire ledger)
def tire_history(request, tire_id):
    tire = get_object_or_404(Tire, pk=tire_id)
    history = TireAssignment.objects.filter(tire=tire).order_by('-assignment_date')
    return render(request, 'tires/tire_history.html', {'tire': tire, 'history': history})

# 3. THE ENGINE (Handles the actual movement)
def tire_assign_submit(request):
    if request.method == "POST":
        tire_id = request.POST.get('tire_id')
        pos_id = request.POST.get('to_position')
        wo_id = request.POST.get('work_order')

        try:
            # Simply create the assignment. 
            # The .save() and .clean() in the model will handle EVERYTHING else.
            TireAssignment.objects.create(
                tire_id=tire_id,
                to_position_id=pos_id if pos_id else None,
                work_order_id=wo_id
            )
            messages.success(request, "Tire movement successfully recorded.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            
    return redirect('tire_history', tire_id=tire_id)

# 4. THE CLEANUP
def assignment_delete(request, pk):
    assignment = get_object_or_404(TireAssignment, pk=pk)
    assignment.delete()
    messages.success(request, "Assignment record removed.")
    return redirect('assignment_list')

# 5. HTMX HELPERS (Optional)
def load_to_positions(request):
    vehicle_id = request.GET.get('vehicle')
    if not vehicle_id:
        # If they select "Warehouse", return an empty option
        return HttpResponse('<option value="">Warehouse (Unmount)</option>')

    positions = TirePosition.objects.filter(
        vehicle_id=vehicle_id,
        mounted_tire__isnull=True,
        vehicle__workorder__status='O'
    ).distinct()

    return render(request, 'tires/partials/position_options.html', {'positions': positions})