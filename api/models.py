from tastypie.resources import ModelResource
from managingsystem.models import Appliance, PowerCalculation, PowerConsumption


class ApplianceResource(ModelResource):
    class Meta:
        queryset = Appliance.objects.all()
        resource_name = "appliances"
        allowed_methods = ['get', 'post', 'delete']


class PowerCalculationResource(ModelResource):
    class Meta:
        queryset = PowerCalculation.objects.all()
        resource_name = "power-calculations"
        allowed_methods = ['get', 'post', 'delete']


class PowerConsumptionResource(ModelResource):
    class Meta:
        queryset = PowerConsumption.objects.all()
        resource_name = "power-consumptions"
        allowed_methods = ['get', 'post', 'delete']


