from django.shortcuts import render, get_object_or_404, redirect
from ..models import Employee
from ..forms.employee_forms import EmployeeForm
from django.contrib import messages

def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'tires/employee_list.html', {
        'employees': employees,
        'form': EmployeeForm() # For the creation modal
    })

def employee_create(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee added successfully.")
        else:
            messages.error(request, f"Error: {form.errors.as_text()}")
    return redirect('employee_list')

def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated {employee.first_name}.")
        else:
            messages.error(request, f"Update failed: {form.errors.as_text()}")
    return redirect('employee_list')

def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.delete()
    messages.success(request, "Employee removed.")
    return redirect('employee_list')