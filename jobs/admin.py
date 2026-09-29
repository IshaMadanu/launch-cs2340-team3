import csv
from django.contrib import admin
from django.http import HttpResponse

# Register your models here.
from .models import Job, Application, Report, CartItem

admin.site.register(CartItem)

@admin.action(description='Export selected to CSV')
def export_to_csv(modeladmin, request, queryset):

    fields = modeladmin.model._meta.fields

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={modeladmin.model.__name__.lower()}.csv'

    writer = csv.writer(response)

    writer.writerow([field.name for field in fields])

    for obj in queryset:
        writer.writerow([
            getattr(obj, field.name)
            for field in fields
        ])

    return response

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'recruiter', 'salary', 'location', 'work_type', 'visa_sponsorship']
    list_filter = ['work_type', 'visa_sponsorship']
    search_fields = ['title', 'skills', 'location']
    actions = [export_to_csv]



@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'job', 'user', 'date']
    list_filter = ['job']
    search_fields = ['note', 'user__username', 'job__title']
    actions = [export_to_csv]


@admin.register(Report)

class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'reason', 'status', 'created_at']
    search_fields = ['reason']
    list_filter = ['status']
    actions = [export_to_csv]

    
