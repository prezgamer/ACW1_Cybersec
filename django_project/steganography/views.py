from django.shortcuts import render, redirect
from .forms import StegImageForm
from .models import StegImage
from stegano import lsb

def encode_message(request):
    if request.method == 'POST':
        form = StegImageForm(request.POST, request.FILES)
        if form.is_valid():
            steg_image = form.save(commit=False)
            input_image = steg_image.image.path
            message = steg_image.hidden_message
            encoded_image_path = input_image.replace('images/', 'images/encoded_')

            # Encoding the message into the image
            encoded_image = lsb.hide(input_image, message)
            encoded_image.save(encoded_image_path)

            steg_image.encoded_image = encoded_image_path
            steg_image.save()
            return redirect('steganography/success.html')  # Redirect to a success page or the encoded image view
    else:
        form = StegImageForm()
    return render(request, 'steganography/encode.html', {'form': form})

def decode_message(request, image_id):
    steg_image = StegImage.objects.get(id=image_id)
    decoded_message = lsb.reveal(steg_image.encoded_image.path)
    return render(request, 'steganography/decode.html', {'decoded_message': decoded_message})

def success(request):
    return render('steganography/success.html')
