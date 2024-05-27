from django import forms
from .models import ImageUpload, Payload

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageUpload
        fields = ['description', 'image']

class PayloadForm(forms.ModelForm):
    class Meta:
        model = Payload
        fields = ['description', 'file']

class LSBSelectionForm(forms.Form):
    num_lsbs = forms.IntegerField(min_value=1, max_value=8, label="Number of LSBs")
