from django.contrib import admin
from .models import Shedule, Message

# Register your models here.
admin.site.register([
    Shedule,
    Message
])