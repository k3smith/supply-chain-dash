from django.db import models
import datetime


class Item(models.Model):
    item_description = models.CharField(max_length=200)
    date_req = models.DateTimeField("date required")
    criticality = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    naics_code = models.CharField(max_length=6, default="")

    def __str__(self):
        return self.item_description
    
    def is_required_soon(self):
        return self.date_req >= datetime.now() - datetime.timedelta(days=1)

class Supplier(models.Model):
    supplier_name = models.CharField(max_length=200)
    naics_code = models.CharField(max_length=6)
    location = models.CharField(max_length=2, default="")
    lat = models.FloatField(max_length=20, default=0)
    lon = models.FloatField(max_length=20, default=0)
    quality = models.IntegerField(default=0)
    delay_risk = models.IntegerField(default=0)

    def __str__(self):
        return self.supplier_name

class SupplierItem(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    requirement = models.ForeignKey(Item, on_delete=models.CASCADE)
    availability = models.DateTimeField("date available")

    def __str__(self):
        return self.supplier.supplier_name + ': ' + self.requirement.item_description

class Coordenadas(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, default='0')
    lat = models.FloatField(max_length=20)
    lon = models.FloatField(max_length=20)
