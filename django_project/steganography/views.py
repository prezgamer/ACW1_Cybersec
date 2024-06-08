from django.core.files.storage import FileSystemStorage
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

def home(request):
    return render(request, 'steganography/home.html')


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


def embed(request):
    global BITS, HIGH_BITS, LOW_BITS, BYTES_PER_BYTE
    if request.method == 'POST':
        form = StegoImageForm(request.POST, request.FILES)
        if form.is_valid():
            stego_image = form.save(commit=False)
            stego_image.original_image = request.FILES['original_image']
            stego_image.save()
            original_image_path = stego_image.original_image.path
            message = stego_image.message
            #Store the entered number into the global variable BITS
            BITS = form.cleaned_data['num_lsbs']
            HIGH_BITS = 256 - (1 << BITS)
            LOW_BITS = (1 << BITS) - 1
            BYTES_PER_BYTE = math.ceil(8 / BITS)
            
            #Define a static file name and path
            static_file_name = f"{stego_image.pk}_stego_image.png"#"stego_image.png"
            output_path = os.path.join(settings.MEDIA_ROOT, "stego_images", static_file_name)

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
    return render(request, 'steganography/embed.html', {'form': form})

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
    global BITS, HIGH_BITS, LOW_BITS, BYTES_PER_BYTE
    if request.method == 'POST':
        form = StegoDecodeForm(request.POST, request.FILES)
        if form.is_valid():
            stego_image = request.FILES['stego_image']
            file_path = os.path.join('stego_images/', stego_image.name)
            #Store the entered number into the global variable BITS
            BITS = form.cleaned_data['num_lsbs']
            HIGH_BITS = 256 - (1 << BITS)
            LOW_BITS = (1 << BITS) - 1
            BYTES_PER_BYTE = math.ceil(8 / BITS)
            
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


# def encode_audio(audio_file_path, hidden_message, output_file_path, lsb_count=1):
#     with wave.open(audio_file_path, 'rb') as audio_file:
#         params = audio_file.getparams()
#         frames = audio_file.readframes(params.nframes)
#         frame_bytes = bytearray(list(frames))
        
#         # Convert the hidden message to bits
#         message_bits = ''.join([format(ord(char), '08b') for char in hidden_message])
#         delimiter = '1' * lsb_count * 2  # Delimiter to indicate end of message
#         message_bits += delimiter
        
#         data_index = 0
#         for i in range(len(frame_bytes)):
#             if data_index < len(message_bits):
#                 bits_to_write = int(message_bits[data_index:data_index + lsb_count], 2)
#                 frame_bytes[i] = (frame_bytes[i] & (255 << lsb_count)) | bits_to_write
#                 data_index += lsb_count
        
#         with wave.open(output_file_path, 'wb') as dest_file:
#             dest_file.setparams(params)
#             dest_file.writeframes(bytes(frame_bytes))
    
#     return frames, frame_bytes

# def decode_audio(audio_file_path, lsb_count=1):
#     with wave.open(audio_file_path, 'rb') as audio_file:
#         frames = audio_file.readframes(audio_file.getnframes())
#         frame_bytes = bytearray(list(frames))
        
#         extracted_bits = ''.join([format(frame_bytes[i] & ((1 << lsb_count) - 1), f'0{lsb_count}b') for i in range(len(frame_bytes))])
        
#         # Find the delimiter to stop reading bits
#         delimiter = '1' * lsb_count * 2
#         end_index = extracted_bits.find(delimiter)
#         if end_index != -1:
#             extracted_bits = extracted_bits[:end_index]
        
#         message_bytes = [extracted_bits[i:i+8] for i in range(0, len(extracted_bits), 8)]
#         message = ''.join([chr(int(byte, 2)) for byte in message_bytes if len(byte) == 8])
        
#         return message

# def testaudio():
#     audio_file_path = "Sample.wav"
#     hidden_message = "Hello, World!"
#     output_file_path = "Encoded_Sample.wav"
#     lsb_count = 8  # Number of LSBs to use for encoding
    
#     original_frames, encoded_frames = encode_audio(audio_file_path, hidden_message, output_file_path, lsb_count)
#     decoded_message = decode_audio(output_file_path, lsb_count)
    
#     print("Original message:", hidden_message)
#     print("Decoded message:", decoded_message)

#     print("DONE")

