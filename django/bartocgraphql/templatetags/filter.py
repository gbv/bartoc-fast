from django import template

register = template.Library()

@register.filter
def get(dictionary: dict, key: str):
    """ Return the value for key """
    return dictionary.get(key)
