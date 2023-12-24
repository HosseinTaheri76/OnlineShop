from django.contrib import admin

# Register your models here.
from .models import ProductComment

@admin.register(ProductComment)
class Admin(admin.ModelAdmin):
    pass

