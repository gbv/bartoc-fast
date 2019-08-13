""" admin.py """

from django.contrib import admin

from .models import Federation, SkosmosInstance, SkosmosQuery, SparqlEndpoint, SparqlQuery

def populate(modeladmin, request, queryset):
    for federation in queryset:
        federation.populate()
populate.short_description = "Populate federation with resources from EXCEL files. Overrides existing resources!"

class FederationAdmin(admin.ModelAdmin):
    actions = [populate]

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
