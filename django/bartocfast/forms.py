from typing import List, Union

from django import forms
from django.db.utils import OperationalError

from .models import Resource
from .schema import Helper

def make_choices() -> List[Resource]:
    """ Return a sorted list of all resources in federation """

    try:
        resources = Helper.make_display_resources()
        resources.sort(key=lambda x: x.name.upper(), reverse=False)
    except OperationalError:
        return []
    else:
        choices = []
        for resource in resources:
            choices.append((resource.name, resource.name))
            
        return choices

CHOICES = make_choices()

class BasicForm(forms.Form):
    """ Basic form """
    
    searchword = forms.CharField(label='Search word:',
                                 widget=forms.TextInput(attrs={'placeholder': 'Enter search word',
                                                               'class': 'form-control'}),
                                 max_length=100,
                                 help_text='Truncation (color*) and wildcards (colo*r) are supported, Boolean operators are not supported',
                                 required=True)

class AdvancedForm(forms.Form):
    """ Advanced form """

    searchword = forms.CharField(label='Search word:',
                                 widget=forms.TextInput(attrs={'placeholder': 'Enter search word',
                                                               'class': 'form-control'}),
                                 max_length=100,
                                 help_text='Truncation (color*) and wildcards (colo*r) are supported, Boolean operators are not supported',
                                 required=True)
    
    maxsearchtime = forms.IntegerField(label='Maximum search time:',                                       
                                       widget=forms.NumberInput(attrs={'placeholder': 'Enter n seconds',
                                                                       'class': 'form-control'}),
                                       max_value=60,
                                       min_value=1,
                                       help_text='1 < n < 60, default n = 5',
                                       required=True)

    duplicates = forms.BooleanField(label='Display duplicates',
                                           widget=forms.CheckboxInput(),
                                           help_text='Check to keep duplicates between resources',
                                           required=False,
                                           label_suffix='')

    disabled = forms.MultipleChoiceField(label='Disable resources',
                                         widget=forms.SelectMultiple(attrs={'style': 'width: 100%', 'size': '15'}), 
                                         help_text='Hold ctrl or shift (or drag with the mouse) to select more than one',
                                         required=False,
                                         choices=CHOICES)


                                          
                                          
    
