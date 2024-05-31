from django import forms
from .models import ImageUpload, Payload

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageUpload
        fields = ['description', 'image']

class PayloadForm(forms.ModelForm):
    class Meta:
        model = Payload
        fields = ['file']

class LSBSelectionForm(forms.Form):
    num_lsbs = forms.IntegerField(min_value=0, max_value=7, label="Number of LSBs")

from .models import StegoImage

class StegoImageForm(forms.ModelForm):
    num_lsbs = forms.IntegerField(min_value=0, max_value=7, label="Number of LSBs")
    class Meta:
        model = StegoImage
        fields = ['original_image', 'message','num_lsbs']
        

class StegoDecodeForm(forms.Form):
    stego_image = forms.ImageField(label="Stego Image")
    num_lsbs = forms.IntegerField(min_value=0, max_value=7, label="Number of LSBs")
