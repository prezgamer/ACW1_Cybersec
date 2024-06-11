from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),

    # Embedding routes
    path('embed/', views.embed, name='embed'),
    path('result/<int:pk>/', views.result, name='result'),
    path('embed_audio/', views.embed_audio, name='embed_audio'),
    path('result_audio/<int:pk>/', views.result_audio, name='result_audio'),
    path('encode_text/', views.encode_text, name='encode_text'),

    # Decoding routes
    path('decode/', views.decode_image, name='decode_image'),
    path('decode_image_results/', views.decode_image_results, name='decode_image_results'),
    path('decode_audio/', views.decode_audio, name='decode_audio'),
    path('decode_text/', views.decode_text, name='decode_text'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)