from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from tires.models import (
    Employee, Supplier, TireStatus, WearType, 
    Service_Type, TirePattern, Vehicle, Tire, 
    TirePosition, WorkOrder, TireAssignment
)

class Command(BaseCommand):
    help = 'Populates fleet data according to the latest model logic'

    def handle(self, *args, **kwargs):
        self.stdout.write("Cleaning database...")
        # Delete in order of dependency to avoid PROTECT errors
        TireAssignment.objects.all().delete()
        TirePosition.objects.all().delete()
        Tire.objects.all().delete()
        WorkOrder.objects.all().delete()
        Vehicle.objects.all().delete()
        TirePattern.objects.all().delete()
        TireStatus.objects.all().delete()
        Supplier.objects.all().delete()
        Employee.objects.all().delete()

        # --- BATCH 1: FOUNDATIONS ---
        self.stdout.write("Creating Employees & Suppliers...")
        mech = Employee.objects.create(first_name="Mike", last_name="Miller", position="Mechanic", email="mike@fleet.com")
        driver = Employee.objects.create(first_name="Dave", last_name="Drive", position="Driver", email="dave@fleet.com")
        
        michelin_supp = Supplier.objects.create(
            name="Michelin Global", contact_person="Sarah", phone="12345", 
            evaluation=5, position="Primary Supplier"
        )

        # Create statuses using the Integer choices defined in your model
        status_new = TireStatus.objects.create(name=1, description="Brand New") # 1 = New Tire
        status_mounted = TireStatus.objects.create(name=2, description="On Vehicle") # 2 = Mounted

        # --- BATCH 2: ASSETS ---
        self.stdout.write("Creating Patterns & Vehicles...")
        highway_pat = TirePattern.objects.create(
            brand_name="Michelin", pattern_code="X-Line", 
            country_of_origin="France", load_index=152, speed_symbol="L",
            road_type='H', axle_type='A', initial_tread_depth=Decimal('18.00'),
            discarding_tread_depth=Decimal('3.00'), ideal_pressure=110
        )

        truck_1 = Vehicle.objects.create(
            license_plate="ABC-123", make="Volvo", year=2022, 
            vehicle_type="Semi", odometer=100000, status="Active",
            tire_configuration="4x2"
        )

        # We need an OPEN Work Order for assignments to pass validation
        open_wo = WorkOrder.objects.create(
            driver=driver, assigned_to=mech, vehicle=truck_1,
            current_odometer=100000, status='O'
        )

        # --- BATCH 3: TIRES & POSITIONS ---
        self.stdout.write("Mounting Tires to Truck 1...")
        for i in range(1, 5):
            # 1. Create the Tire (Unmounted initially)
            tire = Tire.objects.create(
                serial_number=f"SN-{1000 + i}",
                pattern=highway_pat,
                status=status_mounted,
                supplier=michelin_supp,
                purchase_date=timezone.now().date(),
                purchase_price=Decimal('600.00'),
                current_tread_depth=Decimal('18.00'),
                retread_count=0, max_retreads=3,
                size="295/80R22.5"
            )

            # 2. Create the Position
            # Your TirePosition.save() will automatically set tire.current_position = self
            pos = TirePosition.objects.create(
                position_name=f"Pos {i}",
                vehicle=truck_1,
                axle_type="Steer" if i <= 2 else "Drive",
                mounted_tire=tire,
                tire_order=i
            )

            # 3. Create the Initial Assignment (History)
            TireAssignment.objects.create(
                tire=tire,
                from_position=None, # Came from warehouse
                to_position=pos,
                work_order=open_wo,
                start_odometer=open_wo
            )

        # 4. Create Warehouse Tires (Stock)
        self.stdout.write("Creating Warehouse Stock...")
        for i in range(10, 13):
            Tire.objects.create(
                serial_number=f"STOCK-{i}",
                pattern=highway_pat,
                status=status_new,
                supplier=michelin_supp,
                purchase_date=timezone.now().date(),
                purchase_price=Decimal('550.00'),
                current_tread_depth=Decimal('18.00'),
                retread_count=0, max_retreads=3,
                size="295/80R22.5",
                current_position=None # Explicitly warehouse
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated database!'))