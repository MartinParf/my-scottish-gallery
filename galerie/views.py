import json # Přidejte nahoru mezi importy
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PhotoUploadForm
from .models import Photo


def photo_list(request):
    # 1. Filtrování podle přihlášení
    if request.user.is_authenticated:
        photos = Photo.objects.all()
    else:
        photos = Photo.objects.filter(is_public=True)
        
    # 2. Příprava dat pro mapu (Most mezi Pythonem a JavaScriptem)
    map_data = []
    for photo in photos:
        # Přidáme jen fotky, které se nám podařilo lokalizovat
        if photo.latitude and photo.longitude:
            map_data.append({
                'title': photo.title,
                'lat': photo.latitude,
                'lon': photo.longitude,
                'url': photo.image.url if photo.image else '',
                'desc': photo.description if photo.description else '',
                'category': photo.category
            })
            
    # json.dumps převede Python seznam na JSON text
    photos_json = json.dumps(map_data)

    # 3. Pošleme do šablony fotky i JSON data
    return render(request, 'galerie/photo_list.html', {
        'photos': photos,
        'photos_json': photos_json 
    })

def about_us(request):
    return render(request, 'galerie/about.html')

# Dekorátor zajistí, že se sem dostane jen přihlášený uživatel. 
# Pokud není, Django ho samo kopne na přihlašovací stránku.
@login_required 
def upload_photo(request):
    if request.method == 'POST':
        # request.FILES je klíčové! Obsahuje samotný obrázek.
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False) # Zastavíme uložení na vteřinu
            # Zde bychom mohli fotce přiřadit autora (např. photo.owner = request.user)
            photo.save() # Tady se zavolá vaše úžasná komprese a čtení GPS z models.py!
            return redirect('galerie:photo_list') # Po úspěchu šup zpět na mapu
    else:
        form = PhotoUploadForm() # Pokud uživatel jen přišel na stránku, ukážeme prázdný formulář

    return render(request, 'galerie/upload.html', {'form': form})

