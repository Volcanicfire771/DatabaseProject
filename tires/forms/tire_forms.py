from django import forms
from ..models import Tire, TireAssignment, WorkOrder, TirePosition

class TireForm(forms.ModelForm):
    class Meta:
        model = Tire
        # These fields match your screenshot exactly
        fields = [
            'serial_number', 'pattern', 'status', 'supplier', 
            'purchase_date', 'purchase_price', 'current_tread_depth', 
            'current_pressure', 'size', 'retread_count', 
            'max_retreads'
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'purchase_price': forms.NumberInput(attrs={'step': '0.01'}),
            'current_tread_depth': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Automatically apply Bootstrap classes to all fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class TireAssignmentForm(forms.ModelForm):
    class Meta:
        model = TireAssignment
        fields = ['to_position', 'work_order']

    def __init__(self, *args, **kwargs):
        # We can pass a specific 'vehicle' to the form to filter positions
        vehicle = kwargs.pop('vehicle', None)
        super().__init__(*args, **kwargs)

        if vehicle:
            # ONLY show positions for the truck we are currently working on
            # AND only show positions that are currently empty
            self.fields['to_position'].queryset = TirePosition.objects.filter(
                vehicle=vehicle,
                mounted_tire__isnull=True
            )
        
        # Only show OPEN work orders, because you can't move tires on a closed case
        self.fields['work_order'].queryset = WorkOrder.objects.filter(status='Open')