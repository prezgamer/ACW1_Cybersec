from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Map the root URL of the steganography app to the home view
    path('stego/<int:pk>/', views.stego_detail, name='stego_detail'),
]
