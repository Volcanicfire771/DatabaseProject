from django import forms
from ..models import TireStatus

class TireStatusForm(forms.ModelForm):
    class Meta:
        model = TireStatus
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional notes about this status...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        # Apply select specific styling
        self.fields['name'].widget.attrs.update({'class': 'form-select'})