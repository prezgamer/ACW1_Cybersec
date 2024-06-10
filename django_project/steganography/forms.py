from django import forms
#this

from .models import StegoImage

class StegoImageForm(forms.ModelForm):
    num_lsbs = forms.IntegerField(min_value=1, max_value=8, label="Number of LSBs")
    class Meta:
        model = StegoImage
        fields = ['original_image', 'message','num_lsbs']

class StegoDecodeForm(forms.Form):
    stego_image = forms.ImageField(label="Stego Image")
    num_lsbs = forms.IntegerField(min_value=1, max_value=8, label="Number of LSBs")

class AudioEncodeForm(forms.Form):
    audio_file = forms.FileField()
    hidden_message = forms.CharField(max_length=255)
    lsb_count = forms.IntegerField(min_value=1, max_value=16)

class AudioDecodeForm(forms.Form):
    audio_file = forms.FileField()
    lsb_count = forms.IntegerField(min_value=1, max_value=16)
