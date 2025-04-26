from django.contrib import admin
from django.urls import path, include
from api.models import ApplianceResource, PowerCalculationResource, PowerConsumptionResource


appliance_resource = ApplianceResource()
power_calculation_resource = PowerCalculationResource()
power_consumption_resource = PowerConsumptionResource()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("managingsystem.urls")),
    path('api/', include(appliance_resource.urls)),
    path('api/', include(power_calculation_resource.urls)),
    path('api/', include(power_consumption_resource.urls)),
]
