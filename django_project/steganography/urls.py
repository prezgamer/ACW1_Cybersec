from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),  # Map the root URL of the steganography app to the home view
    path('embed/',views.embed,name = 'embed'),
    path('result/<int:pk>/',views.result,name = 'result'),
    path('decode/', views.decode_image, name='decode_image'),  # Add this line
    path('embed_audio/', views.embed_audio, name='embed_audio'),
    path('result_audio/<int:pk>/', views.result_audio, name='result_audio'),
    path('decode_audio/', views.decode_audio, name='decode_audio'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)