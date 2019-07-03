from django import forms

class BasicForm(forms.Form):
    """ Description """
    searchword = forms.CharField(label='searchword', widget=forms.TextInput(attrs={'placeholder': 'search...'}), max_length=100)
