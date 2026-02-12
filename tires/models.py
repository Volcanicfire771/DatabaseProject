from django.db import models
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
# --- Batch 1 ---
# Validations: 1) Email is unique for each employee

class Employee(models.Model): # models.Model is a base class provided by Django (Inheritance)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}" # whenever django needs a human readable name for the object it returns this string

# Validations: 1) Phone & Address can be blank. 2) Evaluation Choices limited to only 5 choices for now
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    position = models.TextField()
    address = models.TextField(blank=True, null=True)
    # Business Logic: Use a choice field for evaluation
    EVALUATION_CHOICES = [
        (1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Excellent'), (5, 'Top Tier') # Better than textfield because 1. Consistency of data. 2. stores the choices as 1,2 or 3 which is cheaper
    ]
    evaluation = models.IntegerField(choices=EVALUATION_CHOICES, default=3)
    
    def __str__(self):
        return f"{self.name} ({self.get_evaluation_display()})"


class TireStatus(models.Model):
    STATUS_CHOICES = [
        (1, 'New Tire'), (2, 'Mounted Tire'), (3, 'Used Tire'), (4, 'For Recycling'), (5, 'Discarded'),(6, 'Re-treaded') # Better than textfield because 1. Consistency of data. 2. stores the choices as 1,2 or 3 which is cheaper
    ]
    name = models.IntegerField(choices=STATUS_CHOICES, default=3)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Tire Statuses" # Change plural from TireStatuss (default by django)

    def __str__(self):
        return self.get_name_display()

class WearType(models.Model):
    wear_type = models.CharField(max_length=100)
    common_cause = models.TextField()
    recovery_scheme = models.TextField()

    def __str__(self):
        return self.wear_type
    

# --- Batch 2 ---


# Validations: 1) unique patternID. 2) ideal pressure/initial_tread/discarding_tread > 0. 
class TirePattern(models.Model):
    pattern_code = models.CharField(max_length=50, blank=True)
    brand_name = models.CharField(max_length=100)
    country_of_origin = models.CharField(max_length=100)
    
    load_index = models.IntegerField(help_text="e.g., 152") # Max weight capacity
    speed_symbol = models.CharField(max_length=5, help_text="e.g., L, M, or K")
    
    # Road Type (e.g., Highway, Off-road, Regional)
    ROAD_TYPE_CHOICES = [
        ('H', 'Highway'),
        ('R', 'Regional'),
        ('U', 'Urban'),
        ('O', 'Off-Road'),
    ]
    road_type = models.CharField(max_length=1, choices=ROAD_TYPE_CHOICES)
    
    # Axle Type - Important for logic!
    AXLE_CHOICES = [
        ('S', 'Steer'),
        ('D', 'Drive'),
        ('T', 'Trailer'),
        ('A', 'All-Position'),
    ]
    axle_type = models.CharField(max_length=1, choices=AXLE_CHOICES)

    # Tread specs
    initial_tread_depth = models.DecimalField(max_digits=5, decimal_places=2)
    discarding_tread_depth = models.DecimalField(max_digits=5, decimal_places=2)
    ideal_pressure = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.brand_name} {self.pattern_code}"

# Validations: 1) Unique Licence plate.
class Vehicle(models.Model):
    license_plate = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    vehicle_type = models.CharField(max_length=50) 
    odometer = models.PositiveIntegerField()
    status = models.TextField()
    tire_configuration = models.TextField()

    # Logic: How many tires should this vehicle have?
    num_op_tires = models.PositiveIntegerField(default=10, verbose_name="Operational Tires")
    num_sp_tires = models.PositiveIntegerField(default=1, verbose_name="Spare Tires")
    @property
    def current_odometer(self):
        # Get the latest WorkOrder for this vehicle to find the current mileage
        latest_work_order = self.workorder_set.order_by('-current_odometer').first()
        if latest_work_order:
            return latest_work_order.current_odometer
        return 0
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.license_plate} ({self.make})"



class Tire(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    
    # Batch 1 Relationships
    pattern = models.ForeignKey('TirePattern', on_delete=models.SET_NULL, null=True, blank=True) 
    status = models.ForeignKey('TireStatus', on_delete=models.SET_NULL, null=True) 
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True) 
    
    # Financial & Technical Data
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_tread_depth = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    current_pressure = models.IntegerField(null=True, blank=True)
    tire_mileage = models.PositiveIntegerField(default=0, help_text="Total KM driven")
    
    size = models.CharField(max_length=50) # Changed to CharField for better indexing/filtering
    retread_count = models.PositiveIntegerField(default=0) 
    max_retreads = models.PositiveIntegerField(default=3)
    
    # Location Snapshot
    current_position = models.ForeignKey(
        'TirePosition', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        help_text="If null, the tire is in the warehouse."
    )

    # Inside your Tire model
    @property
    def total_mileage(self):
        from django.db.models import Sum
        # 1. Sum up all completed/frozen stints
        completed = self.tireassignment_set.aggregate(Sum('stint_distance'))['stint_distance__sum'] or 0
        
        # 2. Calculate "Live" mileage for the active assignment
        active = self.tireassignment_set.filter(removal_date__isnull=True).first()
        live_dist = 0
        
        if active and active.to_position and active.to_position.vehicle:
            # Get the current truck odometer via the property we just created
            truck_odo = active.to_position.vehicle.current_odometer
            start_odo = active.start_odometer.current_odometer
            live_dist = max(0, truck_odo - start_odo)
            
        return completed + live_dist

    def get_active_assignment(self):
        """Returns the current open assignment record for this tire."""
        return self.tireassignment_set.filter(removal_date__isnull=True).last()

    def clean(self):
        """Validates business rules before saving."""
        super().clean()
        if self.retread_count > self.max_retreads:
            raise ValidationError({
                'retread_count': f"Retread count ({self.retread_count}) cannot exceed maximum allowed ({self.max_retreads})."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        brand = self.pattern.brand_name if self.pattern else "Unknown Brand"
        return f"SN: {self.serial_number} - {brand}"
    


# --- Batch 3 ---
class TirePosition(models.Model):
    position_name = models.CharField(max_length=50) # e.g., "Front Left"
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE)
    AXLE_CHOICES = [
        ('S', 'Steer'),
        ('D', 'Drive'),
        ('T', 'Trailer'),
        ('A', 'All-Position'),
    ]
    axle_type = models.CharField(max_length=1, choices=AXLE_CHOICES)
    
    # We use SET_NULL because if the tire is removed, the position still exists
    mounted_tire = models.ForeignKey('Tire', on_delete=models.SET_NULL, null=True, blank=True)

    tire_order = models.PositiveIntegerField()
    is_spare = models.BooleanField(default=False)

    class Meta:
        # The combination of vehicle AND tire_order must be unique
        unique_together = ('vehicle', 'tire_order')

    def save(self, *args, **kwargs):
        tire = self.mounted_tire
        if tire:
            tire.current_position = self
            tire.save()
            
        self.full_clean()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.vehicle.license_plate} - {self.position_name}"


class TireAssignment(models.Model):
    tire = models.ForeignKey('Tire', on_delete=models.CASCADE)
    from_position = models.ForeignKey(
        'TirePosition', 
        related_name='assignments_from', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    to_position = models.ForeignKey(
        'TirePosition', 
        related_name='assignments_to', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    stint_distance = models.FloatField(default=0)
    assignment_date = models.DateTimeField(auto_now_add=True)
    removal_date = models.DateTimeField(null=True, blank=True)
    
    # Capturing mileage via WorkOrder links
    start_odometer = models.ForeignKey(
        'WorkOrder', 
        on_delete=models.SET_NULL, 
        related_name='previous_assignments', 
        null=True, 
        blank=True
    )
    end_odometer = models.ForeignKey(
        'WorkOrder', 
        on_delete=models.SET_NULL, 
        related_name='closing_assignments', 
        null=True, 
        blank=True
    )
    
    work_order = models.ForeignKey('WorkOrder', on_delete=models.SET_NULL, null=True)
    reason_for_removal = models.TextField(blank=True)

   # Inside your TireAssignment class:

    def clean(self):
        from .models import WorkOrder
        super().clean()
        errors = {}

        # 1. TRUTH-FIRST SOURCE ASSIGNMENT (THE FIX)
        # If this is a new record, fetch the CURRENT database state of the tire
        # to find where it's coming from, ignoring any unsaved changes in memory.
        if not self.pk and self.tire_id:
            try:
                # We fetch a fresh copy directly from the DB
                db_tire = type(self.tire).objects.get(pk=self.tire.pk)
                self.from_position = db_tire.current_position
            except type(self.tire).DoesNotExist:
                self.from_position = None

        # 2. VALIDATE TARGET (MOUNTING)
        if self.to_position:
            # Check if destination is occupied by another tire
            if self.to_position.mounted_tire and self.to_position.mounted_tire != self.tire:
                errors['to_position'] = (
                    f"Position {self.to_position} is already occupied by "
                    f"{self.to_position.mounted_tire.serial_number}."
                )

            # Check for Open Work Order on destination vehicle
            has_open_wo = WorkOrder.objects.filter(
                vehicle=self.to_position.vehicle, 
                status='O'
            ).exists()
            if not has_open_wo:
                errors['to_position'] = (
                    f"Vehicle {self.to_position.vehicle.license_plate} has no open Work Order."
                )

        # 3. INTER-VEHICLE MOVE CHECK
        if self.from_position and self.to_position:
            if self.from_position.vehicle != self.to_position.vehicle:
                if not WorkOrder.objects.filter(vehicle=self.from_position.vehicle, status='O').exists():
                    errors['from_position'] = (
                        f"Source vehicle {self.from_position.vehicle.license_plate} "
                        f"must have an open Work Order to record removal mileage."
                    )

        # 4. REMOVAL CHECK (To Warehouse)
        if self.from_position and not self.to_position:
            if not self.work_order:
                errors['work_order'] = "A Work Order is required to record removal mileage."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
            from .models import WorkOrder 
            if self.end_odometer and self.start_odometer:
                self.stint_distance = self.end_odometer.current_odometer - self.start_odometer.current_odometer
            # 1. Run validation to capture the 'from_position' snapshot
            if not self.pk:
                self.full_clean()
            
            is_new = self.pk is None

            if is_new:
                # A. Set the Start Odometer
                if self.work_order and not self.start_odometer:
                    self.start_odometer = self.work_order

                # B. Close previous assignment
                prev_assignment = TireAssignment.objects.filter(
                    tire=self.tire, 
                    removal_date__isnull=True
                ).last()

                if prev_assignment:
                    prev_assignment.removal_date = timezone.now()
                    if prev_assignment.to_position:
                        old_vehicle = prev_assignment.to_position.vehicle
                        closing_wo = WorkOrder.objects.filter(vehicle=old_vehicle, status='O').last()
                        if closing_wo:
                            prev_assignment.end_odometer = closing_wo
                    prev_assignment.save()

            # --- THE FIX FOR tire.current_position ---

            # 2. Update Physical Slots (The TirePosition objects)
            if self.to_position:
                # Mark the new slot as occupied
                type(self.to_position).objects.filter(pk=self.to_position.pk).update(mounted_tire=self.tire)
                # Update the tire instance in memory
                self.tire.current_position = self.to_position
            else:
                # Moving to Warehouse
                self.tire.current_position = None

            # 3. Clear the old physical slot
            if self.from_position and self.from_position != self.to_position:
                type(self.from_position).objects.filter(pk=self.from_position.pk).update(mounted_tire=None)

            # 4. FORCE save the Tire master record
            # We do this specifically to ensure the 'current_position' column in the Tire table updates
            self.tire.save()

            # 5. Finally, save this Assignment record
            super().save(*args, **kwargs)

    

    def __str__(self):
        return f"{self.tire.serial_number} at {self.to_position if self.to_position else 'Warehouse'}"
    
from django.db import models
from django.core.exceptions import ValidationError

class TireInspection(models.Model):
    tire = models.ForeignKey('Tire', on_delete=models.CASCADE)
    position = models.ForeignKey('TirePosition', on_delete=models.SET_NULL, null=True, blank=True)
    inspection_odometer = models.ForeignKey('WorkOrder', on_delete=models.CASCADE)
    inspector = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True)
    inspection_date = models.DateTimeField()    
    
    # Current stats found during inspection
    tread_depth = models.DecimalField(max_digits=5, decimal_places=2)
    pressure = models.IntegerField()
    wear_type = models.ForeignKey('WearType', on_delete=models.SET_NULL, null=True, blank=True)

    # --- SNAPSHOT FIELDS (Frozen History) ---
    # These store the results of the math at the moment of save
    recorded_consumption_rate = models.FloatField(null=True, blank=True)
    recorded_remaining_distance = models.FloatField(null=True, blank=True)
    recorded_current_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    recorded_cost_per_km = models.FloatField(null=True, blank=True)
    recorded_fuel_impact = models.FloatField(null=True, blank=True)

    def get_previous_inspection(self):
        return TireInspection.objects.filter(
            tire=self.tire,
            inspection_date__lt=self.inspection_date
        ).order_by('-inspection_date').first()

    def calculate_performance_snapshot(self):
        """
        Internal logic to calculate metrics based on the current state.
        This is called during save() to freeze the data.
        """
        # 1. Gather Baseline Data
        pattern = self.tire.pattern
        initial_depth = float(pattern.initial_tread_depth)
        discard_depth = float(pattern.discarding_tread_depth)
        ideal_pres = float(pattern.ideal_pressure)
        price = float(self.tire.purchase_price)
        curr_depth = float(self.tread_depth)
        curr_pres = float(self.pressure)
        cto = self.inspection_odometer.current_odometer

        # 2. Find Previous Point (Inspection or Original Mounting)
        prev_insp = self.get_previous_inspection()
        if prev_insp:
            pto = float(prev_insp.inspection_odometer.current_odometer)
            ptd = float(prev_insp.tread_depth)
        else:
            assignment = self.tire.get_active_assignment()
            if assignment and assignment.start_odometer:
                pto = float(assignment.start_odometer.current_odometer)
                ptd = initial_depth
            else:
                pto, ptd = cto, curr_depth # Fallback to avoid zero division

        # 3. Core Math
        distance = cto - pto
        depth_loss = ptd - curr_depth
        
        # Consumption Rate (mm per 10k km)
        crp = (depth_loss / distance * 10000) if distance > 0 and depth_loss > 0 else 0
        
        # Remaining Distance
        rem_dist = ((curr_depth - discard_depth) / crp * 10000) if crp > 0 else 0
        
        # Current Value
        useful_mm = initial_depth - discard_depth
        val = (price * (curr_depth - discard_depth) / useful_mm) if useful_mm > 0 else 0
        
        # Financial Snapshot (CPK)
        cmm = price / useful_mm if useful_mm > 0 else 0
        ckm = (crp / 10000) * cmm 

        # Fuel Impact
        fci = ((ideal_pres - curr_pres) / 10 * 0.4) if ideal_pres > curr_pres else 0

        return {
            'rate': crp,
            'distance': rem_dist,
            'value': max(0, val),
            'cpk': ckm,
            'fuel': fci
        }

    def clean(self):
        if self.inspection_odometer.status == "C":
            raise ValidationError("Vehicle must have an open work order to perform an inspection")

    def save(self, *args, **kwargs):
        self.full_clean()
        
        # 1. Run Calculations and FREEZE them into the recorded fields
        metrics = self.calculate_performance_snapshot()
        
        self.recorded_consumption_rate = metrics['rate']
        self.recorded_remaining_distance = metrics['distance']
        self.recorded_current_value = metrics['value']
        self.recorded_cost_per_km = metrics['cpk']
        self.recorded_fuel_impact = metrics['fuel']

        # 2. Print the Professional Report to Console
        print(f"\n{'='*45}")
        print(f" PERFORMANCE SNAPSHOT: {self.tire.serial_number}")
        print(f"{'='*45}")
        print(f" [WEAR]  Depth: {self.tread_depth}mm | Rate: {self.recorded_consumption_rate:.2f}mm/10k")
        print(f" [LIFE]  Predicted Remaining: {self.recorded_remaining_distance:,.0f} km")
        print(f" [COST]  Cost/km: ${self.recorded_cost_per_km:.4f}")
        print(f" [VALU]  Recorded Asset Value: ${self.recorded_current_value:.2f}")
        print(f"{'='*45}\n")

        # 3. Update the physical Tire asset with latest known status
        tire = self.tire
        tire.current_tread_depth = self.tread_depth
        tire.current_pressure = self.pressure
        tire.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Log: {self.tire.serial_number} ({self.inspection_date.date()})"
    
class WorkOrder(models.Model):
        
    driver = models.ForeignKey('Employee', on_delete=models.SET_NULL, related_name="driver", null=True)
    assigned_to = models.ForeignKey('Employee', on_delete=models.SET_NULL, related_name="assigned_employee", null=True)

    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE)
    
    date_created = models.DateTimeField(auto_now_add=True)
    
    current_odometer = models.PositiveIntegerField()
    
    
    
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True) # blank until work order is closed

    STATUSES = [
        ('O', 'OPENED'),
        ('P', 'PENDING'),
        ('C', 'CLOSED'),
    ]

    status = models.CharField(max_length=1, choices=STATUSES)

    notes = models.TextField(blank=True, null=True) # Notes should never be mandatory
    # # 1. THE RULES
    def clean(self):
        super().clean()
        # Check if another OPEN work order exists for this vehicle
        # We exclude 'self.pk' so that updating an existing WO doesn't trigger the error
        if self.status == 'O':
            exists = WorkOrder.objects.filter(
                vehicle=self.vehicle, 
                status='O'
            ).exclude(pk=self.pk).exists()
            
            if exists:
                raise ValidationError(
                    f"Vehicle {self.vehicle.license_plate} already has an open Work Order. "
                    f"Please close it before opening a new one."
                )

    # 2. THE ENFORCER
    def save(self, *args, **kwargs):
        if self.status == "C":
            vehicle = self.vehicle
            positions = TirePosition.objects.filter(vehicle=vehicle, mounted_tire__isnull=False)

            for pos in positions:
                tire = pos.mounted_tire

                # 1. Get the current active assignment for this tire
                assignment = TireAssignment.objects.filter(
                    tire=tire, 
                    removal_date__isnull=True
                ).last()

                if assignment and assignment.start_odometer:
                    # 2. Calculate the distance traveled during this stint
                    start_miles = assignment.start_odometer.current_odometer
                    end_miles = self.current_odometer # This Work Order's mileage
                    
                    distance_traveled = end_miles - start_miles
                    
                    # 3. Add to the tire's lifetime total
                    if distance_traveled > 0:
                        tire.tire_mileage += distance_traveled
                        tire.save()
        
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"WO {self.id} - {self.vehicle.license_plate}"


class Maintainance_Record(models.Model):
    tire = models.ForeignKey(Tire, on_delete=models.CASCADE, related_name="maintenance_history")    
    service_type = models.ForeignKey('Service_Type', on_delete=models.SET_NULL, null=True, blank=True)
    service_date = models.DateField()
    service_mileage = models.PositiveIntegerField()    
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    service_provider = models.ForeignKey(Employee, on_delete=models.CASCADE)
    notes = models.TextField()

    def __str__(self):
        return f"{self.tire} - {self.service_type}"

class Service_Type(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.name}"