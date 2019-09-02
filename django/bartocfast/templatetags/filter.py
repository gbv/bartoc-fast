from typing import List, Set, Dict, Tuple, Optional, Union

from django import template

from ..models import SkosmosInstance, SparqlEndpoint, LobidResource
from ..utility import VERSION

register = template.Library()

@register.filter
def get_type(resource: Union[SkosmosInstance, SparqlEndpoint]) -> str:
    """ Return the type of a resource"""
    
    if isinstance(resource, SkosmosInstance):
        return "Skosmos"
    if isinstance(resource, SparqlEndpoint):
        return "SPARQL"
    if isinstance(resource, LobidResource):
        return "lobid-gnd API"

@register.filter
def get_len(thing: object) -> int:
    """ Return len(thing) """

    try:
        return len(thing)
    except TypeError:
        return "ERROR: invalid search string! 0"
