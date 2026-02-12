from django.shortcuts import render, get_object_or_404, redirect
from ..models import TirePattern
from ..forms.pattern_forms import TirePatternForm
from django.contrib import messages

def pattern_list(request):
    patterns = TirePattern.objects.all().order_by('brand_name')
    return render(request, 'tires/pattern_list.html', {
        'patterns': patterns,
        'form': TirePatternForm()
    })

def pattern_create(request):
    if request.method == "POST":
        form = TirePatternForm(request.POST)
        if form.is_valid():
            pattern = form.save()
            messages.success(request, f"Pattern {pattern.pattern_code} created.")
        else:
            messages.error(request, f"Error: {form.errors.as_text()}")
    return redirect('pattern_list')

def pattern_update(request, pk):
    pattern = get_object_or_404(TirePattern, pk=pk)
    if request.method == "POST":
        form = TirePatternForm(request.POST, instance=pattern)
        if form.is_valid():
            form.save()
            messages.success(request, "Pattern updated successfully.")
    return redirect('pattern_list')

def pattern_delete(request, pk):
    pattern = get_object_or_404(TirePattern, pk=pk)
    pattern.delete()
    messages.success(request, "Pattern deleted.")
    return redirect('pattern_list')