from typing import List, Set, Dict, Tuple, Optional, Union

from django import template

from ..models import SkosmosInstance, SparqlEndpoint

register = template.Library()

@register.filter
def get_type(resource: Union[SkosmosInstance, SparqlEndpoint]) -> str:
    """ Return the type of a resource"""
    
    if isinstance(resource, SkosmosInstance):
        return "Skosmos"
    if isinstance(resource, SparqlEndpoint):
        return "SPARQL"

@register.filter
def get_len(thing: object) -> int:
    """ Return len(thing) """

    try:
        return len(thing)
    except TypeError:
        return "ERROR: invalid search string! 0"