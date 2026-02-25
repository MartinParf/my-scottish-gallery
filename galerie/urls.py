from django.urls import path
from . import views

app_name = 'galerie'

urlpatterns = [
    path('', views.photo_list, name='photo_list'),
    path('upload/', views.upload_photo, name='upload_photo'),
    path('about/', views.about_us, name='about_us'),  # NEW LINE
]
