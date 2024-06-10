from django import forms
#this

from .models import StegoImage, StegoAudio

class StegoImageForm(forms.ModelForm):
    num_lsbs = forms.IntegerField(min_value=0, max_value=7, label="Number of LSBs")
    class Meta:
        model = StegoImage
        fields = ['original_image', 'message','num_lsbs']

class StegoDecodeForm(forms.Form):
    stego_image = forms.ImageField(label="Stego Image")
    num_lsbs = forms.IntegerField(min_value=0, max_value=7, label="Number of LSBs")

class StegoAudioForm(forms.ModelForm):
    num_lsbs = forms.IntegerField(label='Number of LSBs', min_value=0, max_value=7)
    
    class Meta:
        model = StegoAudio
        fields = ['message_file', 'original_audio', 'message', 'num_lsbs']

class StegoAudioDecodeForm(forms.Form):
    stego_audio = forms.FileField(label='Stego Audio')
    num_lsbs = forms.IntegerField(label='Number of LSBs', min_value=0, max_value=7)