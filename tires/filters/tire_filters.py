import django_filters
from django import forms
from ..models import Tire, TireStatus, TirePattern

class TireFilter(django_filters.FilterSet):
    # Customizing individual fields
    serial = django_filters.CharFilter(
        field_name='serial_number', 
        lookup_expr='icontains', 
        label='Search Serial'
    )

    class Meta:
        model = Tire
        fields = ['status', 'pattern']

    def __init__(self, *args, **kwargs):
        super(TireFilter, self).__init__(*args, **kwargs)
        # Apply Bootstrap classes to every field automatically
        for field in self.filters:
            self.filters[field].field.widget.attrs.update({'class': 'form-control'})
            
        # Specifically for dropdowns, 'form-select' looks better than 'form-control'
        if 'status' in self.filters:
            self.filters['status'].field.widget.attrs.update({'class': 'form-select'})
        if 'pattern' in self.filters:
            self.filters['pattern'].field.widget.attrs.update({'class': 'form-select'})