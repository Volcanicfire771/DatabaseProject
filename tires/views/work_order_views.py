from django.shortcuts import render, get_object_or_404, redirect
from ..models import WorkOrder, Vehicle, Employee
from django.contrib import messages
from ..forms.work_order_forms import WorkOrderForm 

def work_order_list(request):
    orders = WorkOrder.objects.all().order_by('-date_created')
    
    context = {
        'orders': orders,
        'create_form': WorkOrderForm(),
        'vehicles': Vehicle.objects.all(),
        'employees': Employee.objects.all(),
        'orders_opened_count': WorkOrder.objects.filter(status='O').count,
        'orders_closed_count': WorkOrder.objects.filter(status='C').count,
    }
    return render(request, 'tires/work_order_list.html', context)

def work_order_delete(request, pk):
    order = get_object_or_404(WorkOrder, pk=pk)
    order.delete()
    messages.success(request, "Work Order deleted.")
    return redirect('work_order_list')

def work_order_create(request):
    if request.method == "POST":
        form = WorkOrderForm(request.POST)
        if form.is_valid():
            work_order = form.save()
            messages.success(request, f"Work Order #{work_order.id} opened for {work_order.vehicle.license_plate}.")
            return redirect('work_order_list')
        else:
            messages.error(request, "Error opening Work Order. Please check the odometer and fields.")
    
    return redirect('work_order_list')


def work_order_update(request, pk):
    order = get_object_or_404(WorkOrder, pk=pk)
    
    if request.method == "POST":
        order.vehicle_id = request.POST.get('vehicle')
        order.driver_id = request.POST.get('driver') or None
        order.assigned_to_id = request.POST.get('assigned_to') or None
        
        odometer_val = request.POST.get('current_odometer')
        if odometer_val:
            order.current_odometer = int(odometer_val)
        
        order.status = request.POST.get('status')
        order.notes = request.POST.get('notes')
        
        cost_val = request.POST.get('cost')
        if cost_val:
            try:
                order.cost = float(cost_val)
            except ValueError:
                order.cost = 0.00

        order.save()
        messages.success(request, f"Work Order #{order.id} updated.")
        
    return redirect('work_order_list')