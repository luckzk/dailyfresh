from django.contrib import admin
from apps.user import models
# Register your models here.

admin.site.register(models.Address)
admin.site.register(models.User)

