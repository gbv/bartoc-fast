from django import forms

class BasicForm(forms.Form):
    """ Description """
    searchword = forms.CharField(label='searchword', widget=forms.TextInput(attrs={'placeholder': 'Search...'}), max_length=100)
