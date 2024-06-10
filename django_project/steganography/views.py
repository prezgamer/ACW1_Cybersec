from django.core.files.storage import FileSystemStorage
from pydub import AudioSegment
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.conf import settings
from .forms import StegoImageForm, StegoDecodeForm, StegoAudioForm, StegoAudioDecodeForm, StegoTextForm
from .models import StegoImage, StegoAudio
import cv2
import numpy as np
import math
import os
from os import path
from pathlib import Path  # Import Path class from pathlib
import wave


def home(request):
    return render(request, 'steganography/home.html')


BITS = 10000 #change this OG IS 2
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



def encodeAudio(block, data, bits):
    data = ord(data)
    for idx in range(len(block)):
        block[idx] &= HIGH_BITS
        block[idx] |= (data >> (bits * idx)) & LOW_BITS


def convert_to_wav(file_path):
    audio = AudioSegment.from_file(file_path)
    wav_path = os.path.splitext(file_path)[0] + '.wav'
    audio.export(wav_path, format='wav')
    return wav_path  # Return the wav file path

def insertAudio(audio_path: str, msg: str, bits: int = 1):
    audio_path1 = Path(audio_path)  # Create a Path object
    bytes_per_byte = math.ceil(8 / bits)
    flag = "^" 
    with wave.open(audio_path, mode="rb") as audio:
        frame_bytes = list(audio.readframes(audio.getnframes()))
    numpy_audio = np.array(frame_bytes)
    ori_shape = numpy_audio.shape
    max_bytes = len(frame_bytes) // bytes_per_byte
    msg = "{}{}{}".format(len(msg), flag, msg)
    if len(msg) > max_bytes:
        raise BufferError("Message greater than capacity:{}".format(max_bytes))
    data = np.reshape(numpy_audio, -1)
    for idx, val in enumerate(msg):
        encodeAudio(data[idx * bytes_per_byte: (idx + 1) * bytes_per_byte], val, bits)
    frame_bytes = np.reshape(data, ori_shape).tolist()
    filename = audio_path1.stem + "_modified" + audio_path1.suffix  # Modify the filename
    output_path = audio_path1.parent / filename  # Ensure the output path is correct
    if os.path.exists(output_path):
        os.remove(output_path)
    with wave.open(str(output_path), "wb") as newAudio:  # Convert to string
        newAudio.setparams(audio.getparams())
        newAudio.writeframes(bytes(frame_bytes))
    return str(output_path)

def extractAudio(audio_path: str, bits: int = 1):
    bytes_per_byte = math.ceil(8 / bits)
    flag = "^"
    with wave.open(audio_path, mode="rb") as audio:
        frame_bytes = list(audio.readframes(audio.getnframes()))
    numpy_audio = np.array(frame_bytes)
    data = np.reshape(numpy_audio, -1)
    total = data.shape[0]
    res = ""
    idx = 0
    while idx < total // bytes_per_byte:
        ch = decodeAudio(data[idx * bytes_per_byte: (idx + 1) * bytes_per_byte], bits)
        idx += 1
        if ch == flag:
            break
        res += ch
    try:
        end = int(res) + idx
    except ValueError:
        raise ValueError("Input audio isn't correct.")
    if end > total // bytes_per_byte:
        raise ValueError("Input audio isn't correct.")
    secret = ""
    while idx < end:
        secret += decodeAudio(data[idx * bytes_per_byte: (idx + 1) * bytes_per_byte], bits)
        idx += 1
    return secret

def embed_audio(request):
    if request.method == 'POST':
        form = StegoAudioForm(request.POST, request.FILES)
        if form.is_valid():
            stego_audio = form.save(commit=False)
            stego_audio.original_audio = request.FILES['original_audio']
            stego_audio.save()
            original_audio_path = stego_audio.original_audio.path

            if original_audio_path.endswith('.mp3'):
                original_audio_path = convert_to_wav(original_audio_path)

            message = stego_audio.message
            bits = form.cleaned_data['num_lsbs']
            static_file_name = f"{stego_audio.pk}_stego_audio.wav"
            output_path = os.path.join(settings.MEDIA_ROOT, "stego_audio", static_file_name)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            if original_audio_path is not None:
                try:
                    stego_audio_path = insertAudio(original_audio_path, message, bits)
                    stego_audio.stego_audio.name = os.path.join("stego_audio", static_file_name)
                    stego_audio.save()
                    return redirect('result_audio', pk=stego_audio.pk)
                except Exception as e:
                    form.add_error(None, f"Error embedding message in audio: {e}")
            else:
                form.add_error(None, "Error: Original audio path is None")
    else:
        form = StegoAudioForm()
    return render(request, 'steganography/embed_audio.html', {'form': form})


def result_audio(request, pk):
    stego_audio = get_object_or_404(StegoAudio, pk=pk)
    return render(request, 'steganography/result_audio.html', {'stego_audio': stego_audio})

def decode_audio(request):
    if request.method == 'POST':
        form = StegoAudioDecodeForm(request.POST, request.FILES)
        if form.is_valid():
            stego_audio = request.FILES['stego_audio']
            file_path = os.path.join(settings.MEDIA_ROOT, 'stego_audio', stego_audio.name)

            with open(file_path, 'wb+') as destination:
                for chunk in stego_audio.chunks():
                    destination.write(chunk)

            if file_path.endswith('.mp3'):
                file_path = convert_to_wav(file_path)

            bits = form.cleaned_data['num_lsbs']
            try:
                decoded_message = extractAudio(file_path, bits)
                os.remove(file_path)  # Clean up the temporary file
                return render(request, 'steganography/decode_audio_result.html', {'message': decoded_message})
            except Exception as e:
                form.add_error(None, f"Error decoding audio message: {e}")
    else:
        form = StegoAudioDecodeForm()
    return render(request, 'steganography/decode_audio.html', {'form': form})

def decodeAudio(block, bits):
    val = 0
    for idx in range(len(block)):
        val |= (block[idx] & LOW_BITS) << (idx * bits)
    return chr(val)

def encode_text_into_file(cover_file_path, text_payload, lsb_count):
    with open(cover_file_path, 'r') as cover_file:
        cover_text = cover_file.read()

    binary_payload = ''.join(format(ord(char), '08b') for char in text_payload)
    binary_payload += '11111111' * 2  

    encoded_text = []
    binary_index = 0
    for char in cover_text:
        if binary_index < len(binary_payload):
            char_binary = format(ord(char), '08b')
            char_binary = char_binary[:-lsb_count] + binary_payload[binary_index:binary_index + lsb_count]
            encoded_text.append(chr(int(char_binary, 2)))
            binary_index += lsb_count
        else:
            encoded_text.append(char)

    encoded_text = ''.join(encoded_text)
    encoded_file_path = os.path.join(os.path.dirname(cover_file_path), 'encoded_' + os.path.basename(cover_file_path))
    with open(encoded_file_path, 'w') as encoded_file:
        encoded_file.write(encoded_text)

    return encoded_file_path

def encode_text(request):
    if request.method == 'POST':
        form = StegoTextForm(request.POST, request.FILES)
        if form.is_valid():
            cover_file = form.cleaned_data['cover_file']
            text_payload = form.cleaned_data['message']
            lsb_count = form.cleaned_data['num_lsbs']
            message_file = form.cleaned_data['message_file']

            fs = FileSystemStorage()
            filename = fs.save(cover_file.name, cover_file)
            cover_file_path = fs.path(filename)

            if message_file:
                message_filename = fs.save(message_file.name, message_file)
                message_file_path = fs.path(message_filename)
                with open(message_file_path, 'r') as mf:
                    text_payload = mf.read()

            try:
                encoded_file_path = encode_text_into_file(cover_file_path, text_payload, lsb_count)
                response = HttpResponse(open(encoded_file_path, 'rb').read(), content_type='text/plain')
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(encoded_file_path)
                return response
            except Exception as e:
                message = f'Error during encoding: {e}'
                return render(request, 'steganography/encode_text.html', {'form': form, 'message': message})
    else:
        form = StegoTextForm()

    return render(request, 'steganography/encode_text.html', {'form': form})
