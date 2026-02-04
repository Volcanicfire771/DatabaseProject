from django import forms
from ..models import Vehicle

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        # Exclude date_created (auto) and cost (filled at closing)
        fields = [
            'license_plate', 'make', 'year', 
            'vehicle_type', 'odometer', 'status', 'tire_configuration', 'num_op_tires', 'num_sp_tires'
        ]
        # widgets = {
        #     'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe the issue...'}),
        #     'current_odometer': forms.NumberInput(attrs={'placeholder': 'Enter current KM'}),
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})