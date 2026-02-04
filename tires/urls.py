from django.urls import path
from . import views

urlpatterns = [
    # --- Dashboard / Tires ---
    path('', views.tires_list, name='menu_page'),
    path('tires/', views.tires_list, name='tires_list'),
    path('tires/create/', views.tires_create, name='tires_create'),
    path('tires/<int:pk>/update/', views.tires_update, name='tires_update'),
    path('tires/<int:pk>/delete/', views.tires_delete, name='tires_delete'),
    path('tires/<int:tire_id>/history/', views.tire_history, name='tire_history'),
    
    # --- Assignments (Movements) ---
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),
    path('tires/assignments/submit/', views.tire_assign_submit, name='tire_assign_submit'),
    
    # --- Work Orders ---
    path('work-orders/', views.work_order_list, name='work_order_list'),
    path('work-orders/create/', views.work_order_create, name='work_order_create'),
    path('work-orders/<int:pk>/update/', views.work_order_update, name='work_order_update'),
    path('work-orders/<int:pk>/delete/', views.work_order_delete, name='work_order_delete'),
    path('work-order/<int:wo_id>/bulk-inspection/', views.bulk_inspection_view, name='bulk_inspection'),
    
    # --- Vehicles ---
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/create/', views.vehicle_create, name='vehicle_create'),
    path('vehicles/<int:pk>/update/', views.vehicle_update, name='vehicle_update'),
    path('vehicles/<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),

    # --- Employee ---
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/update/', views.employee_update, name='employee_update'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),

    # --- Supplier ---
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/update/', views.supplier_update, name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),

    # --- Tire Status ---
    path('tire-statuses/', views.tire_status_list, name='tire_status_list'),
    path('tire-statuses/create/', views.tire_status_create, name='tire_status_create'),
    path('tire-statuses/<int:pk>/update/', views.tire_status_update, name='tire_status_update'),
    path('tire-statuses/<int:pk>/delete/', views.tire_status_delete, name='tire_status_delete'),

    # --- Tire Wear ---
    path('wear-types/', views.wear_list, name='wear_list'),
    path('wear-types/create/', views.wear_create, name='wear_create'),
    path('wear-types/<int:pk>/update/', views.wear_update, name='wear_update'),
    path('wear-types/<int:pk>/delete/', views.wear_delete, name='wear_delete'),

    # --- Tire Pattern ---
    path('patterns/', views.pattern_list, name='pattern_list'),
    path('patterns/create/', views.pattern_create, name='pattern_create'),
    path('patterns/<int:pk>/update/', views.pattern_update, name='pattern_update'),
    path('patterns/<int:pk>/delete/', views.pattern_delete, name='pattern_delete'),

    # --- Tire Position ---
    path('positions/', views.position_list, name='position_list'),
    path('positions/create/', views.position_create, name='position_create'),
    path('positions/<int:pk>/update/', views.position_update, name='position_update'),
    path('positions/<int:pk>/delete/', views.position_delete, name='position_delete'),
    
    # --- Tire Inspection ---
    # Tire Inspection Management
    path('inspections/', views.inspection_list, name='inspection_list'),
    path('inspections/create/', views.inspection_create, name='inspection_create'),
    path('inspections/<int:pk>/delete/', views.inspection_delete, name='inspection_delete'),
    
    path('inspections/history/<int:tire_id>/', views.inspection_history, name='inspection_history'),

    # --- AJAX ---
    # path('ajax/load-positions/', views.load_positions, name='ajax_load_positions'),
    path('ajax/load-to-positions/', views.load_to_positions, name='ajax_load_to_positions'),

    # --- Placeholder URLs (Redirect to tires for now) ---
    path('employees/', views.tires_list, name='employee_list'),
    path('suppliers/', views.tires_list, name='supplier_list'),
    path('tire-inspections/', views.tires_list, name='tire_inspections_list'),
]