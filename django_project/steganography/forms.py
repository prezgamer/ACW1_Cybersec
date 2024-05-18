from django import forms
from .models import StegImage

class StegImageForm(forms.ModelForm):
    class Meta:
        model = StegImage
        fields = ['image', 'hidden_message']
