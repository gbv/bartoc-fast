from django import forms

class BasicForm(forms.Form):
    """ Description """
    searchterm = forms.CharField(label='search term', widget=forms.TextInput(attrs={'placeholder': 'search term'}), max_length=100)
