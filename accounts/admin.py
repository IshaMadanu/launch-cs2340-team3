import csv
from django.contrib import admin
from django.http import HttpResponse

# Register your models here.
from .models import Account

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

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    actions = [export_to_csv]