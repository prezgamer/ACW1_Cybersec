from django.shortcuts import render, redirect
from .forms import ImageUploadForm, PayloadForm, LSBSelectionForm
from .utils import modify_lsb
from .models import ImageUpload, Payload, StegoObject
from django.core.files.base import ContentFile
from PIL import Image, UnidentifiedImageError
import io

def home(request):
    if request.method == 'POST':
        image_form = ImageUploadForm(request.POST, request.FILES)
        payload_form = PayloadForm(request.POST, request.FILES)
        lsb_form = LSBSelectionForm(request.POST)
        
        if image_form.is_valid() and payload_form.is_valid() and lsb_form.is_valid():
            cover_image = image_form.save()
            payload = payload_form.save()
            num_lsbs = lsb_form.cleaned_data['num_lsbs']

            try:
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
            except UnidentifiedImageError:
                return render(request, 'steganography/home.html', {
                    'image_form': image_form,
                    'payload_form': payload_form,
                    'lsb_form': lsb_form,
                    'error': 'Uploaded file is not a valid image'
                })
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


from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .forms import StegoImageForm
from .models import StegoImage
import cv2
import numpy as np
import math
from os import path
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import StegoDecodeForm


BITS = 6 #change this OG IS 2
HIGH_BITS = 256 - (1 << BITS) #ima change this too
LOW_BITS = (1 << BITS) - 1
BYTES_PER_BYTE = math.ceil(8 / BITS)
FLAG = '%'
TEXTBOX_VALUE = ''

def encode(block, data):
    data = ord(data)
    for idx in range(len(block)):
        block[idx] &= HIGH_BITS
        block[idx] |= (data >> (BITS * idx)) & LOW_BITS

def insert(img_path, msg, output_path):
    img = cv2.imread(img_path, cv2.IMREAD_ANYCOLOR)
    if img is None:
        raise ValueError(f"Could not open or read the image file: {img_path}")
    ori_shape = img.shape
    max_bytes = ori_shape[0] * ori_shape[1] // BYTES_PER_BYTE
    msg = '{}{}{}'.format(len(msg), FLAG, msg)
    assert max_bytes >= len(msg), "Message greater than capacity:{}".format(max_bytes)
    data = np.reshape(img, -1)
    for (idx, val) in enumerate(msg):
        encode(data[idx * BYTES_PER_BYTE: (idx + 1) * BYTES_PER_BYTE], val)
    img = np.reshape(data, ori_shape)
    #filename = path.splitext(img_path)[0] + '_lsb_embeded.png'
    cv2.imwrite(output_path, img)
    #cv2.imwrite(filename, img)
    return output_path
    #return filename

def lsb_view(request):

    if request.method == 'POST':
        form = LSBSelectionForm(request.POST)
        if form.is_valid():
            # Store the entered number into the global variable BITS
            BITS = form.cleaned_data['Number of LSBs']
    else:
        form = LSBSelectionForm()

    #return render(request, 'steganography/testing.html', {'form': form})

def testing(request):
    if request.method == 'POST':
        form = StegoImageForm(request.POST, request.FILES)
        if form.is_valid():
            stego_image = form.save(commit=False)
            stego_image.original_image = request.FILES['original_image']
            stego_image.save()
            original_image_path = stego_image.original_image.path
            message = stego_image.message

             # Define a static file name and path
            static_file_name = "stego_image.png"
            output_path = os.path.join('images/input/', "stego_images", static_file_name)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            try:
                stego_image_path = insert(original_image_path, message,output_path)
                stego_image.stego_image.name =  os.path.join("stego_images", static_file_name)
                stego_image.save()
                return redirect('result', pk=stego_image.pk)
            except Exception as e:
                form.add_error(None, f"Error embedding message: {e}")
    else:
        form = StegoImageForm()
    return render(request, 'steganography/testing.html', {'form': form})

def result(request, pk):
    stego_image = get_object_or_404(StegoImage, pk=pk)
    return render(request, 'steganography/result.html', {'stego_image': stego_image})


#DECODING
def decode(block):
    val = 0
    for idx in range(len(block)):
        val |= (block[idx] & LOW_BITS) << (idx * BITS)
    return chr(val)

def extract(path):
    img = cv2.imread(path, cv2.IMREAD_ANYCOLOR)
    data = np.reshape(img, -1)
    total = data.shape[0]
    res = ''
    idx = 0
    while idx < total // BYTES_PER_BYTE:
        ch = decode(data[idx * BYTES_PER_BYTE: (idx + 1) * BYTES_PER_BYTE])
        idx += 1
        if ch == FLAG:
            break
        res += ch
    end = int(res) + idx
    assert end <= total // BYTES_PER_BYTE, "Input image isn't correct."
    secret = ''
    while idx < end:
        secret += decode(data[idx * BYTES_PER_BYTE: (idx + 1) * BYTES_PER_BYTE])
        idx += 1
    return secret

def decode_image(request):
    if request.method == 'POST':
        form = StegoDecodeForm(request.POST, request.FILES)
        if form.is_valid():
            stego_image = request.FILES['stego_image']
            file_path = os.path.join('images/input', stego_image.name)
            with open(file_path, 'wb+') as destination:
                for chunk in stego_image.chunks():
                    destination.write(chunk)
            try:
                decoded_message = extract(file_path)
                os.remove(file_path)  # Clean up the temporary file
                return render(request, 'steganography/decode_result.html', {'message': decoded_message})
            except Exception as e:
                form.add_error(None, f"Error decoding message: {e}")
    else:
        form = StegoDecodeForm()
    return render(request, 'steganography/decode_image.html', {'form': form})


