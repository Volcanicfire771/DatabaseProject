from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from tires.models import (
    Employee, Supplier, TireStatus, WearType, 
    Service_Type, TirePattern, Vehicle, Tire, TirePosition
)

class Command(BaseCommand):
    help = 'Populates foundational fleet data (Level 1 & 2)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Cleaning old data...")
        # Clear existing data to avoid unique constraint errors
        Tire.objects.all().delete()
        Vehicle.objects.all().delete()
        TirePattern.objects.all().delete()
        Employee.objects.all().delete()

        # --- LEVEL 1: FOUNDATIONS ---
        self.stdout.write("Creating Foundations...")
        
        # 1. Employees
        mech = Employee.objects.create(first_name="Mike", last_name="Miller", position="Senior Mechanic", email="mike@fleet.com")
        driver = Employee.objects.create(first_name="Dave", last_name="Drive", position="Lead Driver", email="dave@fleet.com")

        # 2. Suppliers
        michelin_supp = Supplier.objects.create(name="Michelin Global", contact_person="Sarah Jones", email="sales@michelin.com", evaluation=5)
        local_shop = Supplier.objects.create(name="City Tire Shop", contact_person="Bob", email="bob@citytire.com", evaluation=3)

        # 3. Tire Statuses
        status_new = TireStatus.objects.create(name="New", description="Brand new, never mounted")
        status_used = TireStatus.objects.create(name="In-Use", description="Currently on a vehicle")
        status_scrap = TireStatus.objects.create(name="Scrapped", description="End of life")

        # 4. Wear Types & Service Types
        WearType.objects.create(wear_type="One-sided wear", common_cause="Alignment issue", recovery_scheme="Rotation & Alignment")
        Service_Type.objects.create(name="Rotation", description="Moving tires to different positions")

        # 5. Tire Patterns (The Blueprints)
        highway_pat = TirePattern.objects.create(
            brand_name="Michelin", pattern_code="X-Line-Energy", 
            load_index=152, speed_symbol="L", road_type='H', axle_type='A',
            initial_tread_depth=Decimal('18.00'), discarding_tread_depth=Decimal('3.00'), ideal_pressure=110
        )

        # --- LEVEL 2: ASSETS ---
        self.stdout.write("Creating Vehicles and Tires...")

        # 6. Vehicles
        truck_1 = Vehicle.objects.create(license_plate="ABC-123", make="Volvo", year=2022, vehicle_type="Semi", odometer=150000, status="Active")
        truck_2 = Vehicle.objects.create(license_plate="XYZ-789", make="Scania", year=2023, vehicle_type="Semi", odometer=80000, status="Active")

        # 7. Tires (4 tires for Truck 1)
        for i in range(1, 5):
            tire = Tire.objects.create(
                serial_number=f"SER-{1000 + i}",
                pattern=highway_pat,
                status=status_used,
                supplier=michelin_supp,
                purchase_date=timezone.now().date(),
                purchase_price=Decimal('550.00'),
                current_tread_depth=Decimal('16.50')
            )
            
            # 8. Tire Positions (Mounting the tires to the truck)
            TirePosition.objects.create(
                position_name=f"Axle 1 - Pos {i}",
                vehicle=truck_1,
                axle_type="Steer" if i <= 2 else "Drive",
                mounted_tire=tire,
                tire_order=i
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated Level 1 & 2 data!'))