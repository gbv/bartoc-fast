from .models_base import Query, Resource, Federation
from .models_sparql import SparqlQuery, SparqlEndpoint
from .models_skosmos import SkosmosQuery, SkosmosInstance
from .models_lobid import LobidQuery, LobidResource
from .models_ldapi import LdapiQuery, LdapiEndpoint

### MODELS_RESOURCES = list(SparqlEndpoint.objects.all()) + list(SkosmosInstance.objects.all()) # better method? all things connected to federation?
### MODELS_FEDERATION = Federation.objects.all()[0]
 
