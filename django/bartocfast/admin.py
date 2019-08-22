""" admin.py """

from django.contrib import admin

from .maintenance import Maintenance
from .models import Federation, SkosmosInstance, SkosmosQuery, SparqlEndpoint, SparqlQuery, LobidResource, LobidQuery

def populate(modeladmin, request, queryset):
    Maintenance.populate()
populate.short_description = "Populate federation with resources from .../fixtures"

def selfcheck(modeladmin, request, queryset):
    Maintenance.selfcheck()
selfcheck.short_description = "Disable slow resources in federation"

class FederationAdmin(admin.ModelAdmin):
    actions = [populate, selfcheck]

    def get_actions(self, request):
        """ Disable delete action (drop-down menu) """
        
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        """ Disable delete action (change menu) """
        return False
    
admin.site.register(Federation, FederationAdmin)
admin.site.register(SkosmosInstance)
admin.site.register(SkosmosQuery)
admin.site.register(SparqlEndpoint)
admin.site.register(SparqlQuery)
admin.site.register(LobidResource)
admin.site.register(LobidQuery)
