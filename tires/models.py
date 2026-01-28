from django.db import models
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError

# --- Batch 1 ---
# Validations: 1) Email is unique for each employee

class Employee(models.Model): # models.Model is a base class provided by Django (Inheritance)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}" # whenever django needs a human readable name for the object it returns this string

# Validations: 1) Phone & Address can be blank. 2) Evaluation Choices limited to only 5 choices for now
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    address = models.TextField(blank=True)
    # Business Logic: Use a choice field for evaluation
    EVALUATION_CHOICES = [
        (1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Excellent'), (5, 'Top Tier') # Better than textfield because 1. Consistency of data. 2. stores the choices as 1,2 or 3 which is cheaper
    ]
    evaluation = models.IntegerField(choices=EVALUATION_CHOICES, default=3)
    
    def __str__(self):
        return f"{self.name} ({self.get_evaluation_display()})"


class TireStatus(models.Model):
    name = models.CharField(max_length=50) # e.g., New, Used, Scrapped
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

# Validations: 1) Unique Licence plate. 2)
class Vehicle(models.Model):
    license_plate = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    vehicle_type = models.CharField(max_length=50) 
    odometer = models.PositiveIntegerField()
    status = models.TextField()

    # Logic: How many tires should this vehicle have?
    num_op_tires = models.PositiveIntegerField(default=10, verbose_name="Operational Tires")
    num_sp_tires = models.PositiveIntegerField(default=1, verbose_name="Spare Tires")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.license_plate} ({self.make})"

class Tire(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    
    # FOREIGN KEYS: This links Batch 2 to Batch 1
    pattern = models.ForeignKey(TirePattern, on_delete=models.CASCADE) # CASCADE: If we delete TirePattern all tires associated with the deleted pattern will get deleted.
    status = models.ForeignKey('TireStatus', on_delete=models.SET_NULL, null=True) # SET_NULL: if we delete the status all tires associated with the deleted status will have a null status.
    supplier = models.ForeignKey('Supplier', on_delete=models.PROTECT) # PROTECT: Cannot delete a supplier without deleting all tires associated with that supplier.
    
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_tread_depth = models.DecimalField(max_digits=5, decimal_places=2)

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

    tire_order = models.IntegerField(unique=True)
    is_spare = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.vehicle.license_plate} - {self.position_name}"


class TireAssignment(models.Model):
    tire = models.ForeignKey('Tire', on_delete=models.CASCADE)
    from_position = models.ForeignKey(TirePosition, related_name='assignments_from', on_delete=models.SET_NULL, null=True)
    to_position = models.ForeignKey(TirePosition, related_name='assignments_to', on_delete=models.SET_NULL, null=True)
    assignment_date = models.DateTimeField(auto_now_add=True)
    removal_date = models.DateTimeField(null=True, blank=True)
    
    # Capturing mileage at the moment of change
    start_odometer = models.PositiveIntegerField()
    end_odometer = models.PositiveIntegerField(null=True, blank=True)
    
    removal_mileage = models.PositiveIntegerField()
    reason_for_removal = models.TextField(blank=True)

    #Missing work order & Inspection

    def __str__(self):
        return f"{self.tire.serial_number} moved on {self.assignment_date.date()}"
    
class TireInspection(models.Model):
    tire = models.ForeignKey('Tire', on_delete=models.CASCADE)
    position = models.ForeignKey('TirePosition', on_delete=models.SET_NULL, null=True, blank=True) # blank=true:for django. null=true: for PostgreSQL
    inspection_odometer = models.PositiveIntegerField()
    inspector = models.ForeignKey('Employee', on_delete=models.PROTECT)
    inspection_date = models.DateField()
    
    # Current stats found during inspection
    tread_depth = models.DecimalField(max_digits=5, decimal_places=2)
    pressure = models.IntegerField()
    
    wear_type = models.ForeignKey('WearType', on_delete=models.SET_NULL, null=True, blank=True)
    
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Inspection: {self.tire.serial_number} - {self.inspection_date}"
    
class WorkOrder(models.Model):
    
    wo_id = models.CharField(max_length=50, unique=True, verbose_name="Work Order ID")
    
    driver = models.ForeignKey('Employee', on_delete=models.PROTECT, related_name="driver")
    assigned_to = models.ForeignKey('Employee', on_delete=models.PROTECT, related_name="assigned_employee")

    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE)
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_closed = models.DateTimeField(null=True, blank=True)
    
    current_odometer = models.PositiveIntegerField()
    
    
    
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shift_type = models.CharField(max_length=50)

    STATUSES = [
        ('O', 'OPENED'),
        ('P', 'PENDING'),
        ('C', 'CLOSED'),
    ]

    status = models.CharField(max_length=1, choices=STATUSES)

    notes = models.TextField()

    # 1. THE RULES
    def clean(self):
        super().clean() # Always call this first!
        if self.date_closed and self.date_closed < self.date_created:
            raise ValidationError("A Work Order cannot end before it starts!")

    # 2. THE ENFORCER
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"WO {self.wo_id} - {self.vehicle.license_plate}"


class Maintainance_Record(models.Model):
    tire = models.ForeignKey(Tire,on_delete=models.SET_NULL, null=True, blank=True)
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