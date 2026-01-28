from django.contrib import admin
from .models import (
    Employee, Supplier, TireStatus, WearType, TirePattern, 
    Vehicle, Tire, TirePosition, TireAssignment, TireInspection, 
    Maintainance_Record, WorkOrder, Service_Type
)

# --- Simple Registrations ---
admin.site.register(Employee)
admin.site.register(Supplier)
admin.site.register(TireStatus)
admin.site.register(WearType)
admin.site.register(TirePattern)
admin.site.register(TireAssignment)
admin.site.register(TireInspection)
admin.site.register(WorkOrder)
admin.site.register(Maintainance_Record)
admin.site.register(Service_Type)
# Note: TirePosition is handled as an Inline inside Vehicle, 
# but you can still register it here if you want to edit positions separately.
admin.site.register(TirePosition)

# --- Advanced Registrations ---

@admin.register(Tire)
class TireAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'pattern', 'status', 'current_tread_depth')
    list_filter = ('status', 'pattern')
    search_fields = ('serial_number',)

class TirePositionInline(admin.TabularInline):
    model = TirePosition
    extra = 0 

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'make', 'odometer')
    inlines = [TirePositionInline]