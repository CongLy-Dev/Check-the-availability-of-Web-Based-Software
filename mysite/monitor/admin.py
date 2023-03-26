from django.contrib import admin
from .models import Host, Time


class AbstractModelAdmin(admin.ModelAdmin):
    '''Classe to dont repeat same fields to all'''
    actions = None
    list_per_page = 15


class HostAdmin(AbstractModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'address', 'port', 'network']}),
        ('Daemon Fields', {'fields': [
         'status', 'status_info', 'last_status_change', 'last_check'], 'classes': ['collapse']}),
    ]
    list_display = ('address', 'port', 'name', 'network', 'status')
    search_fields = ['address', 'port', 'name', 'network', 'status']


admin.site.register(Host, HostAdmin)


class TimeAdmin(AbstractModelAdmin):
    fieldsets = [
        (None, {'fields': ['set_hours', 'set_minutes', 'set_seconds', ]})]


admin.site.register(Time, TimeAdmin)

