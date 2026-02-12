from django.shortcuts import render, get_object_or_404, redirect
from ..models import Supplier
from ..forms.supplier_forms import SupplierForm
from django.contrib import messages

def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('-evaluation') # Best rated first
    return render(request, 'tires/supplier_list.html', {
        'suppliers': suppliers,
        'form': SupplierForm()
    })

def supplier_create(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f"Supplier {supplier.name} added.")
        else:
            messages.error(request, "Error creating supplier.")
    return redirect('supplier_list')

def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f"Supplier {supplier.name} updated.")
        else:
            messages.error(request, f"Update failed: {form.errors.as_text()}")
    return redirect('supplier_list')

def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    messages.success(request, "Supplier deleted.")
    return redirect('supplier_list')