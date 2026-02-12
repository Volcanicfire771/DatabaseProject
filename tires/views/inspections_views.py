from django.shortcuts import render, get_object_or_404, redirect
from ..models import TireInspection, Tire, TireAssignment,WearType,WorkOrder
from ..forms.inspection_forms import TireInspectionForm
from django.contrib import messages
from django.utils import timezone

def inspection_list(request):
    inspections = TireInspection.objects.all().select_related(
        'tire', 'inspector', 'inspection_odometer', 'wear_type'
    ).order_by('-inspection_date')
    
    return render(request, 'tires/inspection_list.html', {
        'inspections': inspections,
        'form': TireInspectionForm()
    })

def inspection_create(request):
    if request.method == "POST":
        form = TireInspectionForm(request.POST)
        if form.is_valid():
            # The model's save() method will trigger the performance report printout
            form.save()
            messages.success(request, "Inspection completed and performance metrics updated.")
        else:
            messages.error(request, f"Validation Error: {form.errors.as_text()}")
    return redirect('inspection_list')

def inspection_delete(request, pk):
    inspection = get_object_or_404(TireInspection, pk=pk)
    inspection.delete()
    messages.success(request, "Inspection record removed.")
    return redirect('inspection_list')

def inspection_history(request, tire_id):
    tire = get_object_or_404(Tire, pk=tire_id)
    inspections = TireInspection.objects.filter(tire=tire).order_by('-inspection_date')
    
    return render(request, 'tires/inspection_list.html', {
        'inspections': inspections,
        'selected_tire': tire,
        'form': TireInspectionForm(initial={'tire': tire})
    })


from django.db.models import F

def tire_history(request, tire_id):
    tire = get_object_or_404(Tire, pk=tire_id)
    
    movements = list(TireAssignment.objects.filter(tire=tire))
    inspections = list(TireInspection.objects.filter(tire=tire))
    
    # Combined sorting logic:
    # 1. Date (Newest first)
    # 2. Type (Movements get a 0, Inspections get a 1 -> Movements stay on top in ties)
    # 3. ID (Higher ID means later entry)
    timeline = sorted(
        movements + inspections,
        key=lambda x: (
            x.assignment_date if hasattr(x, 'assignment_date') else x.inspection_date,
            1 if hasattr(x, 'tread_depth') else 0, # Movement=0, Inspection=1
            x.id
        ),
        reverse=True
    )

    return render(request, 'tires/tire_history.html', {
        'tire': tire,
        'timeline': timeline
    })


def bulk_inspection_view(request, wo_id):
    work_order = get_object_or_404(WorkOrder, id=wo_id)
    vehicle = work_order.vehicle
    # Get all tires currently assigned to this vehicle's positions
    active_assignments = TireAssignment.objects.filter(
        to_position__vehicle=vehicle, 
        removal_date__isnull=True
    ).select_related('tire', 'to_position')

    if request.method == 'POST':
        # Logic to loop through the submitted data
        for assignment in active_assignments:
            tread = request.POST.get(f'tread_{assignment.id}')
            pressure = request.POST.get(f'pressure_{assignment.id}')
            wear = request.POST.get(f'wear_{assignment.id}')
            
            if tread and pressure:
                TireInspection.objects.create(
                    tire=assignment.tire,
                    position=assignment.to_position,
                    inspection_odometer=work_order,
                    inspection_date=timezone.now(),
                    tread_depth=tread,
                    pressure=pressure,
                    wear_type_id=wear if wear else None
                )
        
        # Update Work Order Cost and potentially close it
        work_order.cost = request.POST.get('total_cost')
        work_order.save()
        return redirect('work_order_list')

    return render(request, 'tires/bulk_inspection_form.html', {
        'work_order': work_order,
        'assignments': active_assignments,
        'wear_types': WearType.objects.all()
    })



def ajax_load_tires(request):
    wo_id = request.GET.get('inspection_odometer')
    try:
        work_order = WorkOrder.objects.get(id=wo_id)
        # Filter tires currently mounted on the vehicle associated with this Work Order
        tires = Tire.objects.filter(current_position__vehicle=work_order.vehicle)
    except (WorkOrder.DoesNotExist, ValueError):
        tires = Tire.objects.none()

    return render(request, 'tires/partials/tire_options.html', {'tires': tires})