from django.contrib import admin

from .models import OneTimePasswordRequest, OneTimePasswordSetting


# Register your models here.

@admin.register(OneTimePasswordSetting)
class OneTimePasswordSettingAdmin(admin.ModelAdmin):
    
    def has_add_permission(self, request):
        return OneTimePasswordSetting.objects.count() == 0

    def has_delete_permission(self, request, obj=None):
        return False
