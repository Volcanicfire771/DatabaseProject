from django.db import models
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError

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
        return self.name

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

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.license_plate} ({self.make})"

class Tire(models.Model):
    serial_number = models.CharField(max_length=100)
    
    # FOREIGN KEYS: This links Batch 2 to Batch 1
    # CASCADE: If we delete TirePattern all tires associated with the deleted pattern will get deleted.
    # SET_NULL: if we delete the status all tires associated with the deleted status will have a null status.
    # PROTECT: Cannot delete a supplier without deleting all tires associated with that supplier.

    pattern = models.ForeignKey(TirePattern, on_delete=models.SET_NULL,null=True, blank=True) 
    status = models.ForeignKey('TireStatus', on_delete=models.SET_NULL, null=True) 
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL,null=True, blank=True) 
    
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_tread_depth = models.DecimalField(max_digits=5, decimal_places=2,null=True, blank=True)
    current_pressure = models.IntegerField(null=True, blank=True)

    size = models.TextField()
    retread_count = models.PositiveIntegerField() 
    max_retreads = models.PositiveIntegerField()
    tire_mileage = models.IntegerField(default=0)
    current_position = models.ForeignKey('TirePosition', on_delete=models.PROTECT, null=True, blank=True) # if null it means that it is in the warehouse or not attached to any vehicles

    # notes = models.TextField(null=True, blank=True)

    def get_active_assignment(self):
        """Returns the current assignment record for this tire."""
        # We look for the assignment where removal_date is still empty
        return self.tireassignment_set.filter(removal_date__isnull=True).last()

    # cannot retread_count > max_retreads
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"SN: {self.serial_number} - {self.pattern.brand_name}"
    


# --- Batch 3 ---
class TirePosition(models.Model):
    position_name = models.CharField(max_length=50) # e.g., "Front Left"
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE)
    axle_type = models.CharField(max_length=20) # e.g., "Steer", "Drive"
    
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
    from_position = models.ForeignKey(TirePosition, related_name='assignments_from', on_delete=models.SET_NULL, null=True,blank=True)
    to_position = models.ForeignKey(TirePosition, related_name='assignments_to', on_delete=models.SET_NULL, null=True, blank=True)
    assignment_date = models.DateTimeField(auto_now_add=True)
    removal_date = models.DateTimeField(null=True, blank=True)
    
    # Capturing mileage at the moment of change
    start_odometer = models.ForeignKey('WorkOrder', on_delete=models.SET_NULL, related_name='previous_wo', null=True,blank=True) # the previous work order. can be null incase that this is the first assignment
    end_odometer = models.ForeignKey('WorkOrder', on_delete=models.SET_NULL, related_name='current_wo', null=True) # the current work_order
    
    removal_mileage = models.PositiveIntegerField(null=True, blank=True)
    reason_for_removal = models.TextField(blank=True)

    work_order = models.ForeignKey('WorkOrder', on_delete=models.SET_NULL, null=True)

    @staticmethod
    def move_tire(tire, to_position, work_order, reason=""):
        from django.utils import timezone
        
        # 1. CLOSE THE OLD ASSIGNMENT (If it exists)
        active_assignment = TireAssignment.objects.filter(tire=tire, removal_date__isnull=True).last()
        if active_assignment:
            active_assignment.removal_date = timezone.now()
            active_assignment.end_odometer = work_order
            active_assignment.reason_for_removal = reason
            active_assignment.save()
            
            # Important: Clear the old TirePosition link
            if active_assignment.to_position:
                old_pos = active_assignment.to_position
                old_pos.mounted_tire = None
                old_pos.save()

        # 2. UPDATE THE CURRENT STATE
        tire.current_position = to_position
        tire.save()

        if to_position:
            to_position.mounted_tire = tire
            to_position.save()

        # 3. CREATE THE NEW ASSIGNMENT (Only if not moving to Trash/Warehouse)
        if to_position:
            TireAssignment.objects.create(
                tire=tire,
                from_position=active_assignment.to_position if active_assignment else None,
                to_position=to_position,
                start_odometer=work_order,
                work_order=work_order
            )

    def clean(self):
        # 1. Check if the 'to_position' already has a tire
        if self.to_position and self.to_position.mounted_tire:
            # If the tire in that spot isn't the one we are currently moving
            if self.to_position.mounted_tire != self.tire:
                raise ValidationError(
                    f"The position {self.to_position} is already occupied by tire "
                    f"{self.to_position.mounted_tire.serial_number}. "
                    "Please unmount it first."
                )
            
        if self.to_position and self.from_position and self.from_position.vehicle != self.to_position.vehicle:
            #Check if vehicles have work orders
            wo1 =WorkOrder.objects.filter(
            vehicle=self.from_position.vehicle,
            status="O"
        ).first()
            wo2 =WorkOrder.objects.filter(
            vehicle=self.to_position.vehicle,
            status="O"
        ).first()
            
            if not wo1 or not wo2:
                raise ValidationError(
                    f"Both vehicles must have an open work order to perform this operation"
                )
            

    def save(self, *args, **kwargs):
        self.full_clean()
        # Updating the to position to have the tire which automatically updates the tire to be in that position
        self.to_position.mounted_tire = self.tire
        self.to_position.save()

        if self.from_position and self.from_position != self.to_position:
            self.from_position.mounted_tire = None
            self.from_position.save()

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tire.serial_number} moved on {self.assignment_date.date()}"
    
class TireInspection(models.Model):
    tire = models.ForeignKey('Tire', on_delete=models.CASCADE)
    position = models.ForeignKey('TirePosition', on_delete=models.SET_NULL, null=True, blank=True) # blank=true:for django. null=true: for PostgreSQL
    inspection_odometer = models.ForeignKey('WorkOrder', on_delete=models.CASCADE)
    inspector = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True)
    inspection_date = models.DateTimeField()    
    # Current stats found during inspection
    tread_depth = models.DecimalField(max_digits=5, decimal_places=2)
    pressure = models.IntegerField()
    
    wear_type = models.ForeignKey('WearType', on_delete=models.SET_NULL, null=True, blank=True)
    
    # add calculations on the spot


    @property
    def consumption_rate(self):
        prev_insp = self.get_previous_inspection()
        
        if prev_insp:
            # Plan A: Note the change to self.inspection_odometer
            pto = prev_insp.inspection_odometer.current_odometer
            ptd = prev_insp.tread_depth
        else:
            assignment = self.tire.get_active_assignment()
            if assignment and assignment.start_odometer:
                pto = assignment.start_odometer.current_odometer
                ptd = self.tire.pattern.initial_tread_depth
            else:
                return 0 

        cto = self.inspection_odometer.current_odometer # Fix field name
        ctd = self.tread_depth
        
        distance = cto - pto
        depth_loss = ptd - ctd
        
        if distance > 0 and depth_loss > 0:
            # Use float() to avoid Decimal calculation errors
            return (float(depth_loss) / float(distance)) * 10000
        return 0

    @property
    def current_value(self):
        pattern = self.tire.pattern
        useful_life = float(pattern.initial_tread_depth - pattern.discarding_tread_depth)
        remaining_life = float(self.tread_depth - pattern.discarding_tread_depth)
        
        if useful_life > 0:
            percent_left = remaining_life / useful_life
            return float(self.tire.purchase_price) * percent_left
        return 0


    @property
    def remaining_distance(self):
        crp = self.consumption_rate
        dtd = self.tire.pattern.discarding_tread_depth
        ctd = self.tread_depth
        
        if crp > 0:
            return (float(ctd - dtd) / float(crp)) * 10000
        return 0

    

    def get_previous_inspection(self):
        
        return TireInspection.objects.filter(
            tire=self.tire,
            inspection_date__lt=self.inspection_date # 'lt' means 'less than' (earlier)
        ).order_by('-inspection_date').first() # Get the newest one of the older ones

    def clean(self):
        if self.inspection_odometer.status == "C":
            raise ValidationError(
                    f"Vehicle must have an open work order to perform an inspection"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        # 1. Repeating variables pulled to the top
        pattern = self.tire.pattern
        initial_depth = float(pattern.initial_tread_depth)
        discard_depth = float(pattern.discarding_tread_depth)
        ideal_pres = float(pattern.ideal_pressure)
        price = float(self.tire.purchase_price)
        curr_depth = float(self.tread_depth)
        curr_pres = float(self.pressure)
        
        # 2. Calculated Properties (Cast to float for safety)
        crp = float(self.consumption_rate)
        rtd = float(self.remaining_distance)
        val = float(self.current_value)
        
        # 3. Custom Equations
        ttm = self.tire.tire_mileage
        
        # Cost per Millimeter (cmm)
        useful_mm = initial_depth - discard_depth
        cmm = price / useful_mm if useful_mm > 0 else 0
        
        # Cost per Kilometer (ckm)
        ckm = 10 * (crp/10000) * cmm 
        
        # Fuel Consumption Impact (fci)
        fci = ((ideal_pres - curr_pres) / 10 * 0.4) if ideal_pres > curr_pres else 0
        
        # Financial Loss due to Pressure (flc)
        # last assignment made on the tire -->  work order --> current odometer
        ptm = self.inspection_odometer.current_odometer - TireAssignment.objects.filter(tire=self.tire).first().work_order.current_odometer
        flc = fci * (ptm / 100) 
        
        # Standard variables for printing
        dto = discard_depth
        
        # Current Tire Value (ctv)
        if (initial_depth - dto) > 0:
            ctv = (curr_depth - dto) / (initial_depth - dto) * price
        else:
            ctv = 0
            
        # Remaining Distance (btd)
        btd = (curr_depth - dto) / crp * 10000 if crp > 0 else 0

        # 4. Professional Print Statement
        print(f"\n{'='*45}")
        print(f" PERFORMANCE REPORT: {self.tire.serial_number}")
        print(f"{'='*45}")
        print(f" [WEAR]  Depth: {curr_depth}mm | Rate: {crp:.2f}mm/10k")
        print(f" [LIFE]  Predicted Remaining: {btd:,.0f} units")
        print(f" [COST]  CPmm: ${cmm:.2f} | Cost/km: ${ckm:.4f}")
        print(f" [FUEL]  Pressure Loss: {ideal_pres - curr_pres:.1f} PSI")
        print(f"         Fuel Impact Factor: {fci:.4f}")
        print(f" [VALU]  Current Asset Value: ${ctv:.2f}")
        print(f"{'='*45}\n")

        # 5. History handling
        prev = self.get_previous_inspection()
        if prev:
            prev_depth = prev.tread_depth
            prev_pressure = prev.pressure
        else:
            prev_depth = self.tire.current_tread_depth
            prev_pressure = self.tire.current_pressure

        print(f"DEBUG: Comparison -> Prev: {prev_depth}mm / Now: {self.tread_depth}mm")

        # 6. Update Tire and Commit
        tire = self.tire
        tire.current_tread_depth = self.tread_depth
        tire.current_pressure = self.pressure
        tire.save()

        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Inspection: {self.tire.serial_number} - {self.inspection_date}"
    
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
    # def clean(self):
    #     super().clean() # Always call this first!
    #     if self.date_closed and self.date_closed < self.date_created:
    #         raise ValidationError("A Work Order cannot end before it starts!")

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