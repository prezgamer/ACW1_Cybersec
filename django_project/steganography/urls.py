from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Map the root URL of the steganography app to the home view
    path('stego/<int:pk>/', views.stego_detail, name='stego_detail'),
    path('testing/',views.testing,name = 'testing'),
    path('result/<int:pk>/',views.result,name = 'result'),
    path('decode/', views.decode_image, name='decode_image'),  # Add this line

]
