from django.contrib import admin
from .models import Shedule, Notification

# Register your models here.
admin.site.register([
    Shedule,
    Notification
])