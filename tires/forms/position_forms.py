from django import forms
from ..models import TirePosition, Vehicle, Tire

class TirePositionForm(forms.ModelForm):
    class Meta:
        model = TirePosition
        # We include mounted_tire here so the view can process it, 
        # but we will hide it in the Create modal HTML.
        fields = ['position_name', 'vehicle', 'axle_type', 'mounted_tire', 'tire_order', 'is_spare']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['is_spare'].widget.attrs.update({'class': 'form-check-input'})