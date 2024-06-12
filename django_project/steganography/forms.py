from django import forms
from .models import StegoImage, StegoAudio, StegoDecodeImage, StegoDecodeAudio

class StegoImageForm(forms.ModelForm):
    num_lsbs = forms.IntegerField(min_value=0, max_value=7, label="Number of LSBs")
    class Meta:
        model = StegoImage
        fields = ['message_file','original_image','num_lsbs']
    

class StegoImageDecodeForm(forms.ModelForm):
    stego_image = forms.ImageField()
    num_lsbs = forms.IntegerField(min_value=0, max_value=7, label="Number of LSBs")

    class Meta:
        model = StegoDecodeImage
        fields = ['reader_file']


class StegoAudioForm(forms.ModelForm):
    num_lsbs = forms.IntegerField(label='Number of LSBs', min_value=0, max_value=7)
    
    class Meta:
        model = StegoAudio
        fields = ['message_file', 'original_audio', 'num_lsbs']


class StegoAudioDecodeForm(forms.ModelForm):
    stego_audio = forms.FileField(label='Stego Audio')
    num_lsbs = forms.IntegerField(label='Number of LSBs', min_value=0, max_value=7)

    class Meta:
        model = StegoDecodeAudio
        fields = []


class StegoTextForm(forms.Form):
    cover_file = forms.FileField(label="Select Cover File")
    message = forms.CharField(widget=forms.Textarea, label="Message to Embed")
    num_lsbs = forms.IntegerField(min_value=0, max_value=7, label="Number of LSBs")
    message_file = forms.FileField(label="Message File", required=False)


class DecodeTextForm(forms.Form):
    stego_file = forms.FileField(label="Select Stego Text File")
    num_lsbs = forms.IntegerField(min_value=0, max_value=7, label="Number of LSBs")
    