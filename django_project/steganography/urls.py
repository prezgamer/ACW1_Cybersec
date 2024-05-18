from django.urls import path
from . import views

urlpatterns = [
    path('encode/', views.encode_message, name='steganography-home'),
    path('success/', views.success, name='success'),
    path('decode/<int:image_id>/', views.decode_message, name='decode_message'),
]