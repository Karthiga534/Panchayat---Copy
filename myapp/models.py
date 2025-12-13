from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Signup(models.Model):
    username = models.CharField(max_length=100, null=True)
    phoneno = models.CharField(max_length=100, null=True)
    conpass = models.CharField(max_length=255, null=True)
    password = models.CharField(max_length=255, null=True)  # Increase length for hashed password
    address = models.CharField(max_length=100, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def set_password(self, raw_password):
        """Hash and save password"""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Check password"""
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.username} - {self.phoneno}"


class Login(models.Model):
    username=models.CharField(max_length=100,null=True)
    phoneno=models.CharField(max_length=100,null=True)
    password=models.CharField(max_length=100,null=True)
    role=models.CharField(max_length=100, null=True)

    # signup model for supervisor


# complaint model request model
# request and complaint
class Complaint(models.Model):
    user = models.CharField(max_length=100,null=True)
    phone = models.CharField(max_length=100,null=True)
    address = models.TextField(max_length=255, null=True)
    location = models.CharField(max_length=255, null=True)
    complaint_type = models.CharField(max_length=100, null=True)
    description = models.TextField(max_length=500, null=True)
    file = models.FileField(upload_to='complaints/', blank=True, null=True)
    date_time = models.DateTimeField(default=timezone.now)
    supervisor_name= models.CharField(max_length=100,null=True)
    status = models.CharField(
        max_length=20,
        default='unverified'
    )

    def _str_(self):
        return f"{self.user.name} - {self.complaint_type}"



class Supervisor(models.Model):
    supervisor_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    gender = models.CharField(max_length=10)
    supervisor_id = models.CharField(max_length=50, unique=True)
    area = models.CharField(max_length=100)
    password = models.CharField(max_length=128)
    conpass = models.CharField(max_length=100, null=True)

class Request(models.Model):
    REQUEST_TYPES = [
        ("Public Safety", "Public Safety"),
        ("Sanitation / Hygiene", "Sanitation / Hygiene"),
        ("Road / Traffic Issues", "Road / Traffic Issues"),
        ("Electricity / Water Supply", "Electricity / Water Supply"),
        ("Government Services", "Government Services"),
        ("Others", "Others"),
    ]
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPES)
    other_type = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(max_length=500, null=True)
    supervisor_name = models.CharField(max_length=100, null=True)
    area = models.CharField(max_length=100, null=True)
    date_time= models.DateTimeField(auto_now_add=True, null=True)
    file = models.FileField(upload_to='requests/', blank=True, null=True)
    status = models.CharField(
        max_length=20,
        default='unverified'
    )

    def _str_(self):
        return f"{self.name} - {self.request_type}"


# models for posts, achievements, tasks
from django.db import models
from django.utils import timezone

class Post(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='posts/images/', null=True, blank=True)
    video = models.FileField(upload_to='posts/videos/', null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    deleted_by = models.TextField(blank=True, default="")

class Achievement(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    achieved_on = models.DateField(default=timezone.now)
    image = models.ImageField(upload_to='achievements/', blank=True, null=True)
    
# Task model
class Task(models.Model):
    STATUS_CHOICES = (
        ('verfied', 'Verified'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    assigned_date = models.DateField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.title

class Admins(models.Model):
    username=models.CharField(max_length=100, null=True)
    password=models.CharField(max_length=100, null=True)
class Area(models.Model):
    name = models.CharField(max_length=100, unique=True)

class ComplaintSupervisor(models.Model):
    STATUS_CHOICES = [
        ('unverified', 'Unverified'),
        ('verified', 'Verified'),
    ]
    user = models.CharField(max_length=100,null=True)  # Name of the person
    phone = models.CharField(max_length=20,null=True)
    address = models.TextField(max_length=100, null=True)
    location = models.CharField(max_length=100, null=True)  # Area
    complaint_type = models.CharField(max_length=200, null=True)  # Type of complaint
    supervisor_name = models.CharField(max_length=100, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='unverified'
    )
class EOSignup(models.Model):
    eo_number = models.CharField(max_length=20, unique=True, null=True)
    password = models.CharField(max_length=128, null=True)  # store plain text only if really necessary; otherwise hash
    conpass = models.CharField(max_length=128, null=True)
    area = models.CharField(max_length=100, null=True)
    eo_name = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=15, unique=True, null=True)
    address = models.TextField(null=True)
class Forgotpassword(models.Model):
    otp=models.CharField(max_length=10,null=True)
    phoneno=models.CharField(max_length=100,null=True)
    username=models.CharField(max_length=100,null=True)
    newpassword=models.CharField(max_length=100,null=True)
    confirmpassword=models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
