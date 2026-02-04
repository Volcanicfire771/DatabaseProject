from django import forms
from ..models import Supplier

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'position', 'address', 'evaluation']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Physical office address...'}),
            'position': forms.TextInput(attrs={'placeholder': 'e.g. Sales Manager'}),
            'evaluation': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        # Ensure the dropdown uses form-select for better Bootstrap appearance
        self.fields['evaluation'].widget.attrs.update({'class': 'form-select'})