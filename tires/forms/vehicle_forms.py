from django import forms
from ..models import Vehicle

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'license_plate', 'make', 'year', 
            'vehicle_type', 'odometer', 'status', 
            'tire_configuration', 'num_op_tires', 'num_sp_tires'
        ]
        widgets = {
            'tire_configuration': forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g., 2-4-4'}),
            'license_plate': forms.TextInput(attrs={'placeholder': 'ABC-1234'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Apply base bootstrap class
            field.widget.attrs.update({'class': 'form-control'})
            
            # Use form-select for dropdowns to get the chevron arrow
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs.update({'class': 'form-select'})