import json  # Make sure json is imported at the top
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PhotoUploadForm, PhotoEditForm
from .models import Photo
from django_ratelimit.decorators import ratelimit


def photo_list(request):
    # 1. Filter depending on authentication status
    if request.user.is_authenticated:
        photos = Photo.objects.all()
    else:
        photos = Photo.objects.filter(is_public=True)

    # --- NOVÉ: Získání unikátních roků pro filtry ---
    # Najde všechny fotky, které mají datum, vycucne z nich jen rok, seřadí je sestupně a odstraní duplikáty
    available_years_qs = Photo.objects.exclude(date_taken__isnull=True).dates('date_taken', 'year', order='DESC')
    available_years = [d.year for d in available_years_qs]

    # 2. Prepare data for the map (bridge between Python and JavaScript)
    map_data = []
    for photo in photos:
        # Add only photos that we managed to geolocate
        if photo.latitude and photo.longitude:
            
            # Nastavení URL adres pro mapu a detail
            thumb_url = ''
            full_url = ''
            
            if photo.image:
                full_url = photo.image.url
                # Pokud adresa obsahuje /upload/ (Cloudinary), vygenerujeme miniaturu
                if '/upload/' in full_url:
                    thumb_url = full_url.replace('/upload/', '/upload/w_300,h_300,c_fill,q_auto,f_auto/')
                else:
                    thumb_url = full_url

            map_data.append({
                'title': photo.title,
                'lat': photo.latitude,
                'lon': photo.longitude,
                'thumb_url': thumb_url,  # ZDE POSÍLÁME MINIATURU
                'full_url': full_url,    # ZDE POSÍLÁME ORIGINÁL
                'desc': photo.description if photo.description else '',
                'category': photo.category,
                # --- NOVÉ: Přidáváme data o čase do JSONu pro JavaScript ---
                'year': photo.date_taken.year if photo.date_taken else None,
                'date_formatted': photo.date_taken.strftime('%d. %m. %Y') if photo.date_taken else ''
            })
            
    # json.dumps converts the Python list into JSON text
    photos_json = json.dumps(map_data)

    # 3. Send both photos and JSON data to the template
    return render(request, 'galerie/photo_list.html', {
        'photos': photos,
        'photos_json': photos_json,
        'available_years': available_years  # Posíláme roky do šablony
    })

def about_us(request):
    return render(request, 'galerie/about.html')

# The decorator ensures that only an authenticated user can access this view.
# If not authenticated, Django will automatically redirect to the login page.
@login_required 
@ratelimit(key='ip', rate='5/m', block=True)
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

# 1. Zobrazení tabulky všech fotek
@login_required
def manage_photos(request):
    # Vytáhneme všechny fotky seřazené od nejnovější
    photos = Photo.objects.all().order_by('-timestamp')
    return render(request, 'galerie/manage_photos.html', {'photos': photos})

# 2. Úprava konkrétní fotky
@login_required
def edit_photo(request, pk):
    # Najde fotku podle ID, nebo vyhodí chybu 404
    photo = get_object_or_404(Photo, pk=pk)
    
    if request.method == 'POST':
        # Nahráváme data do formuláře a říkáme mu, ať upraví EXISTUJÍCÍ instanci
        form = PhotoEditForm(request.POST, instance=photo)
        if form.is_valid():
            form.save()
            return redirect('galerie:manage_photos')
    else:
        # Prázdný formulář už předvyplněný současnými daty
        form = PhotoEditForm(instance=photo)
        
    return render(request, 'galerie/edit_photo.html', {'form': form, 'photo': photo})

# 3. Smazání fotky
@login_required
def delete_photo(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    if request.method == 'POST':
        photo.delete() # Toto díky vašemu kódu v models.py smaže i soubor na Cloudinary!
        return redirect('galerie:manage_photos')
    
    # Pokud se sem dostane bez POST metody, ukážeme mu potvrzovací stránku
    return render(request, 'galerie/confirm_delete.html', {'photo': photo})