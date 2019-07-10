from django import forms

class BasicForm(forms.Form):
    """ Basic form """
    
    searchword = forms.CharField(label='Search word:',
                                 widget=forms.TextInput(attrs={'placeholder': 'Enter search word',
                                                               'class': 'form-control'}),
                                 max_length=100,
                                 help_text='Boolean operators are not implemented',
                                 required=True)

class AdvancedForm(forms.Form):
    """ Advanced form """
    
    searchword = forms.CharField(label='Search word:',
                                 widget=forms.TextInput(attrs={'placeholder': 'Enter search word',
                                                               'class': 'form-control'}),
                                 max_length=100,
                                 help_text='Boolean operators are not implemented',
                                 required=True)
    
    maxsearchtime = forms.IntegerField(label='Maximum search time:',
                                       widget=forms.NumberInput(attrs={'placeholder': 'Enter n seconds',
                                                                       'class': 'form-control'}),
                                       max_value=60,
                                       min_value=1,
                                       help_text="1 < n < 60",
                                       required=False)
    
