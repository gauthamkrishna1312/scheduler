from django.contrib import admin
from .models import Shedule, Message2Manager

# Register your models here.
admin.site.register([
    Shedule,
    Message2Manager
])