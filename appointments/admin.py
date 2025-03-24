from django.contrib import admin
from .models import Appointment, AppointmentDocument
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'appointment_type', 'date_time', 'duration')
    list_filter = ('appointment_type', 'date_time')
    search_fields = ('title', 'name', 'email', 'description')
    date_hierarchy = 'date_time'


@admin.register(AppointmentDocument)
class AppointmentDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'appointment', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('title', 'description', 'appointment__title')