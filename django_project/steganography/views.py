from django.shortcuts import render, redirect
from .forms import ImageUploadForm

# Create your views here.
def home(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = ImageUploadForm()
    return render(request, 'steganography/home.html', {'form': form})

def success(request):
    return render(request, 'steganography/success.html')