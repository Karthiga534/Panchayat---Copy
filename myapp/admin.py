from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Admins)
admin.site.register(Supervisor)
admin.site.register(Complaint)
admin.site.register(Request)