from django.contrib import admin

# Register your models here.
from .models import Location, LocationEntry

admin.site.register(Location)
admin.site.register(LocationEntry)
