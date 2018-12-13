from django.contrib import admin

# Register your models here.

from ss_app.models import Event, Appointment, Days, TimeSlots, Staff, Client, Notes, FocusAreas

class TimeSlotsAdmin(admin.ModelAdmin):
    list_display = ['day', 'start_time', 'end_time', 'available', 'assigned_to']
    list_filter = ['day', 'assigned_to']


admin.site.register(Event)
admin.site.register(Appointment)
admin.site.register(Days)
admin.site.register(TimeSlots)
admin.site.register(Staff)
admin.site.register(Client)
admin.site.register(Notes)
admin.site.register(FocusAreas)
