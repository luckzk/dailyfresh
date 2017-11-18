from django.contrib import admin
from apps.order import models

# Register your models here.

admin.site.register(models.OrderInfo)
admin.site.register(models.OrderGoods)

