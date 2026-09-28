from django.contrib import admin

# Register your models here.
from .models import Job, Application, Report, CartItem
admin.site.register(Job)
admin.site.register(Application)
admin.site.register(CartItem)

class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'reason', 'status', 'created_at']
    search_fields = ['reason']
    list_filter = ['status']
admin.site.register(Report)
