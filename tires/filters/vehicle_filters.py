import django_filters
from django import forms
from ..models import Vehicle

class VehicleFilter(django_filters.FilterSet):
    # Customizing individual fields
    serial = django_filters.CharFilter(
        field_name='license_plate', 
        lookup_expr='icontains', 
        label='Search License Plate'
    )

    # vehicle_type = django_filters.ChoiceFilter(
    #     choices=Vehicle.TYPE_CHOICES, # Uses the list from your model
    #     label="Vehicle Category",
    #     empty_label="All Categories"
    # )

    class Meta:
        model = Vehicle
        fields = ['status', 'vehicle_type']

    def __init__(self, *args, **kwargs):
        super(VehicleFilter, self).__init__(*args, **kwargs)
        # Apply Bootstrap classes to every field automatically
        for field in self.filters:
            self.filters[field].field.widget.attrs.update({'class': 'form-control'})
            
        # Specifically for dropdowns, 'form-select' looks better than 'form-control'
        # if 'status' in self.filters:
        #     self.filters['status'].field.widget.attrs.update({'class': 'form-select'})
        # if 'vehicle_type' in self.filters:
        #     self.filters['vehicle_type'].field.widget.attrs.update({'class': 'form-select'})