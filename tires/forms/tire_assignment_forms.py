from django import forms
from ..models import TireAssignment, TirePosition, WorkOrder, Vehicle, Tire

class TireAssignmentForm(forms.ModelForm):
    # Extra field for the UI to select the Vehicle first
    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.all(),
        required=False,
        label="Select Vehicle"
    )

    class Meta:
        model = TireAssignment
        fields = ['tire', 'from_position', 'to_position', 'work_order']

    def clean(self):
        cleaned_data = super().clean()
        vehicle = cleaned_data.get('vehicle')
        to_position = cleaned_data.get('to_position')

        # We ONLY care if the NEW position (to_position) belongs to the 
        # vehicle we are currently working on.
        if vehicle and to_position:
            if to_position.vehicle != vehicle:
                raise forms.ValidationError(
                    f"The selected position ({to_position}) does not belong to {vehicle}."
                )
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # --- Defensive Programming: Check if fields exist before modifying ---
        # This prevents KeyErrors when Django Admin sets these to 'readonly'

        if 'from_position' in self.fields:
            self.fields['from_position'].required = False
            self.fields['from_position'].empty_label = "Warehouse"
            
            # Handle the dynamic queryset filter
            if 'tire' in self.data:
                try:
                    tire_id = self.data.get('tire')
                    tire = Tire.objects.get(pk=tire_id)
                    if tire.current_position:
                        self.fields['from_position'].queryset = TirePosition.objects.filter(pk=tire.current_position.pk)
                    else:
                        self.fields['from_position'].queryset = TirePosition.objects.none()
                except (ValueError, TypeError, Tire.DoesNotExist):
                    pass

        if 'to_position' in self.fields:
            self.fields['to_position'].required = False
            self.fields['to_position'].empty_label = "Warehouse"
        
        if 'work_order' in self.fields:
            # Only show open work orders
            self.fields['work_order'].queryset = WorkOrder.objects.filter(status='O')