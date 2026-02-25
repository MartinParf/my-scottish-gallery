import json  # Make sure json is imported at the top
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PhotoUploadForm
from .models import Photo


def photo_list(request):
    # 1. Filter depending on authentication status
    if request.user.is_authenticated:
        photos = Photo.objects.all()
    else:
        photos = Photo.objects.filter(is_public=True)
        
    # 2. Prepare data for the map (bridge between Python and JavaScript)
    map_data = []
    for photo in photos:
        # Add only photos that we managed to geolocate
        if photo.latitude and photo.longitude:
            map_data.append({
                'title': photo.title,
                'lat': photo.latitude,
                'lon': photo.longitude,
                'url': photo.image.url if photo.image else '',
                'desc': photo.description if photo.description else '',
                'category': photo.category
            })
            
    # json.dumps converts the Python list into JSON text
    photos_json = json.dumps(map_data)

    # 3. Send both photos and JSON data to the template
    return render(request, 'galerie/photo_list.html', {
        'photos': photos,
        'photos_json': photos_json 
    })

def about_us(request):
    return render(request, 'galerie/about.html')

# The decorator ensures that only an authenticated user can access this view.
# If not authenticated, Django will automatically redirect to the login page.
@login_required 
def upload_photo(request):
    if request.method == 'POST':
        # request.FILES is crucial: it contains the uploaded image file.
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)  # Briefly stop before saving
            # Here we could assign an owner to the photo (e.g. photo.owner = request.user)
            photo.save()  # This triggers the compression and GPS extraction logic in models.py
            return redirect('galerie:photo_list')  # After success, redirect back to the map
    else:
        form = PhotoUploadForm()  # If user just opened the page, show an empty form

    return render(request, 'galerie/upload.html', {'form': form})

