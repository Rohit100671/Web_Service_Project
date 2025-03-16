from djongo import models
from bson import ObjectId
from django.contrib.auth.models import AbstractUser


#-------------------- For LogIn, New Register and LogOut ---------------------------#


# For Amdin, Provider and Client LogIn purpose -
class User(AbstractUser):
    _id = models.ObjectIdField(default=ObjectId, primary_key=True)
    ROLE_CHOICES = [
        ('admin', 'admin'),
        ('provider', 'provider'),
        ('client', 'client'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='webserviceapp_users',
        blank=True,
        help_text="The groups this user belongs to."
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='webserviceapp_users_permissions',
        blank=True,
        help_text="Specific permissions for this user."
    )

    def __str__(self):
        return f"{self.username} - {self.role}"



#-------------------------------- For Provider -------------------------------------#


# For the Provider Services -
class ProviderService(models.Model):

    _id = models.ObjectIdField(default=ObjectId, primary_key=True)

    SERVICE_TYPES = [
        ('plumbing', 'plumbing'),
        ('electrical', 'electrical'), 
    ]    

    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('approved', 'approved'),
        ('rejected', 'rejected'),
    ]

    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Add image and video fields
    image = models.ImageField(upload_to='service_images/', blank=True, null=True)
    video = models.FileField(upload_to='service_videos/', blank=True, null=True)
    time_slot = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.name} - {self.get_service_type_display()}"
    

    class Meta:
        db_table='Provider_services'



#--------------------------- For Clients -----------------------------------#


# For the Booking History - 
class BookingHistory(models.Model):
    _id = models.ObjectIdField(default=ObjectId, primary_key=True)
    service_name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=50)
    booked_at = models.DateTimeField(auto_now_add=True)
    user_id = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.user_name} booked {self.service_name}"
    
    class Meta:
        db_table = "booking_history"


# For the Reiew System - 
from bson import ObjectId
from djongo.models import ObjectIdField

class ServiceReview(models.Model):
    _id = ObjectIdField(default=ObjectId, primary_key=True)
    user_name = models.CharField(max_length=100) 
    user_id = models.CharField(max_length=100)
    provider_name = models.CharField(max_length=250)
    provider_id =  models.CharField(max_length=250)
    service_type=models.CharField(max_length=250) 
    service_name = models.CharField(max_length=100)
    service_id = models.CharField(max_length=100)
    rating = models.IntegerField()
    review = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='ServiceReview'

    def __str__(self):
        return f"{self.user_name} - {self.service_provider} ({self.rating})"



