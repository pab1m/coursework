from django.contrib import admin
from .models import Appliance, PowerCalculation, PowerConsumption

admin.site.register(Appliance)
admin.site.register(PowerCalculation)
admin.site.register(PowerConsumption)
