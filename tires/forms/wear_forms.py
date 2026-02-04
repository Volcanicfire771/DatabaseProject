from django import forms
from ..models import WearType

class WearTypeForm(forms.ModelForm):
    class Meta:
        model = WearType
        fields = ['wear_type', 'common_cause', 'recovery_scheme']
        widgets = {
            'wear_type': forms.TextInput(attrs={'placeholder': 'e.g., Shoulder Wear, Camber Wear'}),
            'common_cause': forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g., Under-inflation or overloading'}),
            'recovery_scheme': forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g., Adjust pressure and rotate tires'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})