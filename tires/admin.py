from django.contrib import admin
from django.utils.html import format_html
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
admin.site.register(Maintainance_Record)
admin.site.register(Service_Type)
admin.site.register(TirePosition)

# --- Inlines ---

class TirePositionInline(admin.TabularInline):
    model = TirePosition
    extra = 0

class TireAssignmentInline(admin.TabularInline):
    model = TireAssignment
    extra = 0
    # Everything in history should be read-only to prevent audit tampering
    readonly_fields = ('from_position', 'to_position', 'work_order', 'assignment_date', 'removal_date', 'stint_distance_display')
    fields = ('from_position', 'to_position', 'work_order', 'assignment_date', 'removal_date', 'stint_distance_display')

    def stint_distance_display(self, obj):
        return f"{obj.stint_distance:,.0f} km"
    stint_distance_display.short_description = "Distance in Stint"

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

# --- Admin Actions ---

@admin.action(description="Move selected tires to Garage (Warehouse)")
def move_to_garage(modeladmin, request, queryset):
    last_wo = WorkOrder.objects.filter(status='O').last() 
    if not last_wo:
        modeladmin.message_user(request, "Error: No open Work Order found to attach the move to.", level='ERROR')
        return

    for tire in queryset:
        # Only move if it's actually mounted somewhere
        if tire.current_position:
            # The logic inside TireAssignment.save() or our custom move logic 
            # should handle closing the old stint.
            TireAssignment.objects.create(
                tire=tire,
                from_position=tire.current_position,
                to_position=None,
                work_order=last_wo,
                reason_for_removal="Bulk move via Admin Action"
            )
    modeladmin.message_user(request, f"Selected tires moved to Warehouse under WO #{last_wo.id}.")

# --- Advanced Registrations ---

@admin.register(TireInspection)
class TireInspectionAdmin(admin.ModelAdmin):
    list_display = ('tire', 'inspection_date', 'tread_depth', 'pressure', 'recorded_value_display')
    readonly_fields = (
        'recorded_consumption_rate', 'recorded_remaining_distance', 
        'recorded_current_value', 'recorded_cost_per_km', 'recorded_fuel_impact'
    )
    list_filter = ('inspection_date', 'wear_type')

    def recorded_value_display(self, obj):
        return f"${obj.recorded_current_value:,.2f}"
    recorded_value_display.short_description = "Value at Log"

@admin.register(Tire)
class TireAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'pattern', 'current_location', 'total_km', 'status_badge')
    list_filter = ('status', 'pattern')
    search_fields = ('serial_number',)
    inlines = [TireAssignmentInline]
    actions = [move_to_garage]

    def current_location(self, obj):
        pos = obj.current_position
        return f"{pos.vehicle.license_plate} ({pos.position_name})" if pos else "Warehouse"

    def total_km(self, obj):
        # Calling the property we created in the model
        return f"{obj.total_mileage:,.0f} km"
    total_km.short_description = "Lifetime Mileage"

    def status_badge(self, obj):
        colors = {'New': '#28a745', 'Used': '#fd7e14', 'Scrapped': '#dc3545', 'Retreaded': '#007bff'}
        color = colors.get(str(obj.status), 'black')
        return format_html('<span style="color: {}; font-weight: bold;">● {}</span>', color, obj.status)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'make', 'get_odo')
    inlines = [TirePositionInline]

    def get_odo(self, obj):
        return f"{obj.current_odometer:,.0f} km"
    get_odo.short_description = "Current Odometer"

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'current_odometer', 'cost_display', 'status', 'date_created')
    list_filter = ('status', 'date_created')
    
    def cost_display(self, obj):
        return f"${obj.cost:,.2f}" if obj.cost else "$0.00"
    cost_display.short_description = "Total Cost"

@admin.register(TireAssignment)
class TireAssignmentAdmin(admin.ModelAdmin):
    list_display = ('tire', 'from_position', 'to_position', 'stint_distance', 'assignment_date')
    readonly_fields = ('stint_distance',)