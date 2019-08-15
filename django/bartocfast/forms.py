from typing import List, Union

from django import forms
from django.db.utils import OperationalError

from .models import SkosmosInstance, SparqlEndpoint

def make_choices() -> List[Union[SkosmosInstance, SparqlEndpoint]]:
    """ Return list of all resources in federation """

    try:
        resources = list(SparqlEndpoint.objects.all()) + list(SkosmosInstance.objects.all())
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
                                 help_text='Truncation (color*) and wildcards (col*r) are supported, Boolean operators are not supported',
                                 required=True)

class AdvancedForm(forms.Form):
    """ Advanced form """

    searchword = forms.CharField(label='Search word:',
                                 widget=forms.TextInput(attrs={'placeholder': 'Enter search word',
                                                               'class': 'form-control'}),
                                 max_length=100,
                                 help_text='Truncation (color*) and wildcards (col*r) are supported, Boolean operators are not supported',
                                 required=True)
    
    maxsearchtime = forms.IntegerField(label='Maximum search time:',
                                       widget=forms.NumberInput(attrs={'placeholder': 'Enter n seconds',
                                                                       'class': 'form-control'}),
                                       max_value=60,
                                       min_value=1,
                                       help_text='1 < n < 60, default n = 5',
                                       required=False)

    duplicates = forms.BooleanField(label='Display duplicates',
                                           widget=forms.CheckboxInput(),
                                           help_text='Check to keep duplicates between resources',
                                           required=False,
                                           label_suffix='')

    disabled = forms.MultipleChoiceField(label='Disable resources',
                                          widget=forms.SelectMultiple(attrs={'style': 'width: 100%'}),
                                          help_text='Hold ctrl or shift (or drag with the mouse) to select more than one',
                                          required=False,
                                          choices=CHOICES)
                                          
                                          
    
