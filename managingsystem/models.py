from django.db import models
from django.contrib.auth.models import User


class Appliance(models.Model):
    STATUS_CHOICES = (
        ('ввімкнений', 'Ввімкнений'),
        ('вимкнений', 'Вимкнений'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brand_name = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100)
    power = models.FloatField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand_name} {self.product_name}"


class PowerCalculation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brand_name = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100)
    power = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField()


class PowerConsumption(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    total_power = models.FloatField()

    def __str__(self):
        return f"{self.user} - {self.date} - {self.total_power}"
