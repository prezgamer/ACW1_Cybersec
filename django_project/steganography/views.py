from django.shortcuts import render, redirect
from .forms import ImageUploadForm, PayloadForm, LSBSelectionForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import modify_lsb
from .models import ImageUpload, Payload, StegoObject
from django.core.files.base import ContentFile
from PIL import Image
import io
import json
import os
from django.conf import settings
from django.core.files.storage import default_storage

def home(request):
    if request.method == 'POST':
        image_form = ImageUploadForm(request.POST, request.FILES)
        payload_form = PayloadForm(request.POST, request.FILES)
        lsb_form = LSBSelectionForm(request.POST)
        
        if image_form.is_valid() and payload_form.is_valid() and lsb_form.is_valid():
            cover_image = image_form.save()
            payload = payload_form.save()
            num_lsbs = lsb_form.cleaned_data['num_lsbs']

            # Process the cover image and payload
            cover_image_data = Image.open(cover_image.image)
            payload_data = payload.file.read()
            
            # Convert the cover image to bytes
            cover_image_io = io.BytesIO()
            cover_image_data.save(cover_image_io, format=cover_image_data.format)
            cover_image_bytes = cover_image_io.getvalue()

            # Perform LSB modification
            stego_image_bytes = modify_lsb(cover_image_bytes, payload_data, num_lsbs)

            # Save the stego image
            stego_image_io = io.BytesIO(stego_image_bytes)
            stego_image = Image.open(stego_image_io)
            stego_image_io.seek(0)
            stego_object = StegoObject(cover_image=cover_image, payload=payload)
            stego_object.stego_image.save(f'stego_{cover_image.image.name}', ContentFile(stego_image_io.read()))
            stego_object.save()

            return redirect('stego_detail', pk=stego_object.pk)
    else:
        image_form = ImageUploadForm()
        payload_form = PayloadForm()
        lsb_form = LSBSelectionForm()

    return render(request, 'steganography/home.html', {
        'image_form': image_form,
        'payload_form': payload_form,
        'lsb_form': lsb_form
    })

def stego_detail(request, pk):
    stego_object = StegoObject.objects.get(pk=pk)
    return render(request, 'steganography/stego_detail.html', {'stego_object': stego_object})
