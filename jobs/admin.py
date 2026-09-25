from django.contrib import admin

# Register your models here.
from .models import Job, Application
admin.site.register(Job)
admin.site.register(Application)
from .models import Job, Report
admin.site.register(Job)

class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'reason', 'status', 'created_at']
    search_fields = ['reason']
    list_filter = ['status']
admin.site.register(Report)
