from django import forms
from .models import ImageUpload, Payload, StegoImage
#this
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

class StegoImageForm(forms.ModelForm):
    file = forms.FileField()
    num_lsbs = forms.IntegerField(min_value=0, max_value=7, label="Number of LSBs")
    class Meta:
        model = StegoImage
        fields = ['original_image', 'message','num_lsbs', 'file']

class StegoDecodeForm(forms.Form):
    stego_image = forms.ImageField(label="Stego Image")
    num_lsbs = forms.IntegerField(min_value=0, max_value=7, label="Number of LSBs")

class AudioEncodeForm(forms.Form):
    audio_file = forms.FileField()
    hidden_message = forms.CharField(max_length=255)
    lsb_count = forms.IntegerField(min_value=1, max_value=16)

class AudioDecodeForm(forms.Form):
    audio_file = forms.FileField()
    lsb_count = forms.IntegerField(min_value=1, max_value=16)
