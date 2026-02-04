from django import forms
from ..models import TirePattern

class TirePatternForm(forms.ModelForm):
    class Meta:
        model = TirePattern
        fields = '__all__'
        widgets = {
            'initial_tread_depth': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'discarding_tread_depth': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'ideal_pressure': forms.NumberInput(attrs={'placeholder': 'PSI'}),
            'pattern_code': forms.TextInput(attrs={'placeholder': 'e.g. R250, M726'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        # Fix selects for Bootstrap
        self.fields['road_type'].widget.attrs.update({'class': 'form-select'})
        self.fields['axle_type'].widget.attrs.update({'class': 'form-select'})