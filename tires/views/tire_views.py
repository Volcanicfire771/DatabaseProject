from django.shortcuts import render, redirect, get_object_or_404
from ..models import Tire, TirePattern, TireStatus, Supplier, TirePosition
from ..forms import TireForm
from ..filters import TireFilter

def tires_list(request):
    # Keep your optimized queryset
    tires = Tire.objects.all().select_related('status', 'pattern', 'supplier', 'current_position')
    
    # IMPORTANT: Link the filter to your 'tires' variable so it actually filters!
    tire_filter = TireFilter(request.GET, queryset=tires)
    
    context = {
        
        'tires': tire_filter.qs, 
        
        'create_form': TireForm(),
        'tire_patterns': TirePattern.objects.all(),
        'tire_statuses': TireStatus.objects.all(),
        'suppliers': Supplier.objects.all(),
        'tire_positions': TirePosition.objects.all(),
        
        # Quick Stats
        'total_count': tires.count(),
        
        'active_count': tires.filter(status_id=2).count(), 
        
        # Filter
        'filter': tire_filter,
    }
    return render(request, 'tires/tires_list.html', context)

def tires_create(request):
    if request.method == "POST":
        form = TireForm(request.POST)
        if form.is_valid():
            form.save()
            # Success! Redirect back to the hub
            return redirect('tires_list')
        else:
            # If there are errors (like a duplicate serial number), 
            # you might want to handle showing them, but for today, 
            # we'll redirect back to keep it simple.
            return redirect('tires_list')
    return redirect('tires_list')

def tires_update(request, pk):
    # 1. Find the specific tire or 404 if it doesn't exist
    tire = get_object_or_404(Tire, pk=pk)
    
    if request.method == "POST":
        # 2. Fill the form with POST data, but link it to the existing 'tire' instance
        form = TireForm(request.POST, instance=tire)
        
        if form.is_valid():
            form.save()
            # 3. Success! Go back to the list
            return redirect('tires_list')
            
    # If something goes wrong or it's a GET request, just go back
    return redirect('tires_list')

from django.shortcuts import get_object_or_404, redirect
from ..models import Tire

def tires_delete(request, pk):
    # 1. Fetch the tire
    tire = get_object_or_404(Tire, pk=pk)
    
    # 2. Delete it
    tire.delete()
    
    # 3. Go back to the list
    return redirect('tires_list')