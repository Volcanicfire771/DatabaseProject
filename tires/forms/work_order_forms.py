from django import forms
from ..models import WorkOrder

class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        # Exclude date_created (auto) and cost (filled at closing)
        fields = [
            'vehicle', 'driver', 'assigned_to', 
            'current_odometer', 'status', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe the issue...'}),
            'current_odometer': forms.NumberInput(attrs={'placeholder': 'Enter current KM'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})