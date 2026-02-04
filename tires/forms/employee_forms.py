from django import forms
from ..models import Employee

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'middle_name', 'last_name', 'position', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'example@company.com'}),
            'position': forms.TextInput(attrs={'placeholder': 'e.g. Workshop Manager'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})