from django import forms
from ..models import TirePosition, Vehicle, Tire

class TirePositionForm(forms.ModelForm):
    # Force the field to be a ChoiceField at the form level
    axle_type = forms.ChoiceField(choices=[
        ('S', 'Steer'),
        ('D', 'Drive'),
        ('T', 'Trailer'),
        ('A', 'All-Position'),
    ])

    class Meta:
        model = TirePosition
        fields = ['position_name', 'vehicle', 'axle_type', 'mounted_tire', 'tire_order', 'is_spare']
        widgets = {
            # This forces the field to use a Select dropdown with your choices
            'axle_type': forms.Select(choices=TirePosition.AXLE_CHOICES),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['is_spare'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['axle_type'].widget.attrs.update({'class': 'form-select'})