from django.contrib import admin

# Register your models here.
from .models import Client, Order, Warehouse, Box

admin.site.register(Client)
admin.site.register(Order)
admin.site.register(Warehouse)
admin.site.register(Box)