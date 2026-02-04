from django.shortcuts import render, get_object_or_404, redirect
from ..models import WearType
from ..forms.wear_forms import WearTypeForm
from django.contrib import messages

def wear_list(request):
    wears = WearType.objects.all()
    return render(request, 'tires/wear_list.html', {
        'wears': wears,
        'form': WearTypeForm()
    })

def wear_create(request):
    if request.method == "POST":
        form = WearTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Wear type added successfully.")
        else:
            messages.error(request, f"Error: {form.errors.as_text()}")
    return redirect('wear_list')

def wear_update(request, pk):
    wear = get_object_or_404(WearType, pk=pk)
    if request.method == "POST":
        form = WearTypeForm(request.POST, instance=wear)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated {wear.wear_type}.")
    return redirect('wear_list')

def wear_delete(request, pk):
    wear = get_object_or_404(WearType, pk=pk)
    wear.delete()
    messages.success(request, "Wear type deleted.")
    return redirect('wear_list')