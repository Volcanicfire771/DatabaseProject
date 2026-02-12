from django import forms
from ..models import TireInspection, WorkOrder, Tire

class TireInspectionForm(forms.ModelForm):
    class Meta:
        model = TireInspection
        fields = [
            'tire', 'inspector', 'inspection_date', 
            'tread_depth', 'pressure', 'wear_type', 'inspection_odometer'
        ]
        widgets = {
            'inspection_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'tread_depth': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'e.g. 12.50'}),
            'pressure': forms.NumberInput(attrs={'placeholder': 'PSI'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['tire'].queryset = Tire.objects.none()

        if 'inspection_odometer' in self.data:
            try:
                # 1. Get the Work Order ID from the form data
                wo_id = int(self.data.get('inspection_odometer'))
                
                # 2. Find the vehicle associated with that Work Order
                # We use .get() to get the single object, then access its vehicle
                work_order = WorkOrder.objects.get(id=wo_id)
                target_vehicle = work_order.vehicle

                # 3. Filter tires that are currently mounted on that specific vehicle
                # This assumes your Tire model has a 'current_position' that links to a 'vehicle'
                self.fields['tire'].queryset = Tire.objects.filter(
                    current_position__vehicle=target_vehicle
                ).order_by('serial_number')

            except (ValueError, TypeError, WorkOrder.DoesNotExist):
                pass  # If ID is invalid or WO doesn't exist, keep queryset as .none()

        self.fields['inspection_odometer'].queryset = WorkOrder.objects.filter(
            status='O'
        ).select_related('vehicle')
        
        # Optional: Customize how the label looks in the dropdown
        self.fields['inspection_odometer'].empty_label = "--- Select an Open Work Order ---"

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        # Use select-specific styling for foreign keys
        self.fields['tire'].widget.attrs.update({'class': 'form-select'})
        self.fields['wear_type'].widget.attrs.update({'class': 'form-select'})
        self.fields['inspection_odometer'].widget.attrs.update({'class': 'form-select'})