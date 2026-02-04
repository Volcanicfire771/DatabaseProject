from django import forms
from ..models import TireInspection

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
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        # Use select-specific styling for foreign keys
        self.fields['tire'].widget.attrs.update({'class': 'form-select'})
        self.fields['wear_type'].widget.attrs.update({'class': 'form-select'})
        self.fields['inspection_odometer'].widget.attrs.update({'class': 'form-select'})