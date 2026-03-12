from django.urls import path
from . import views

app_name = 'galerie'

urlpatterns = [
    path('', views.photo_list, name='photo_list'),
    path('upload/', views.upload_photo, name='upload_photo'),
    path('about/', views.about_us, name='about_us'),  # NEW LINE

    # --- NOVÉ CESTY PRO EDIT PHOTO HUB ---
    path('manage/', views.manage_photos, name='manage_photos'),
    path('manage/<int:pk>/edit/', views.edit_photo, name='edit_photo'),
    path('manage/<int:pk>/delete/', views.delete_photo, name='delete_photo'),
    path('manage/export-zip/', views.export_photos_zip, name='export_photos_zip'),
    path('manage/bulk-upload/', views.bulk_upload, name='bulk_upload'),
]
