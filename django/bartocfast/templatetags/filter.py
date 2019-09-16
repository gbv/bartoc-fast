from typing import List, Set, Dict, Tuple, Optional, Union

from django import template

from ..models import Resource, SkosmosInstance, SparqlEndpoint, LobidResource, LdapiEndpoint
from ..utility import VERSION

register = template.Library()

@register.filter
def get_type(resource: Resource) -> str:
    """ Return the type of a resource"""
    
    if isinstance(resource, SkosmosInstance):
        return "Skosmos"
    if isinstance(resource, SparqlEndpoint):
        return "SPARQL"
    if isinstance(resource, LobidResource):
        return "lobid-gnd API"
    if isinstance(resource, LdapiEndpoint):
        return "Linked-Data-API"

@register.filter
def get_len(thing: object) -> int:
    """ Return len(thing) """

    try:
        return len(thing)
    except TypeError:
        return "ERROR: invalid search string! 0"
