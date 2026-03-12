import json  # Make sure json is imported at the top
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PhotoUploadForm, PhotoEditForm
from .models import Photo, Album
from django_ratelimit.decorators import ratelimit
from django.contrib import messages
import zipfile
import io
import urllib.request
from django.http import HttpResponse
from django.db.models import Count



def photo_list(request):
    if request.user.is_authenticated:
        photos = Photo.objects.all()
    else:
        photos = Photo.objects.filter(is_public=True)
        
    # Získáme roky pro filtry
    available_years_qs = Photo.objects.exclude(date_taken__isnull=True).dates('date_taken', 'year', order='DESC')
    available_years = [d.year for d in available_years_qs]
    
    # --- NOVÉ: Získáme jen ta alba, ve kterých už nějaká fotka fyzicky je ---
    albums = Album.objects.filter(photos__isnull=False).distinct().order_by('-created_at')

    map_data = []
    for photo in photos:
        if photo.latitude and photo.longitude:
            thumb_url = ''
            full_url = ''
            if photo.image:
                full_url = photo.image.url
                if '/upload/' in full_url:
                    thumb_url = full_url.replace('/upload/', '/upload/w_300,h_300,c_fill,q_auto,f_auto/')
                else:
                    thumb_url = full_url

            map_data.append({
                'title': photo.title,
                'lat': photo.latitude,
                'lon': photo.longitude,
                'thumb_url': thumb_url,
                'full_url': full_url,
                'desc': photo.description if photo.description else '',
                'category': photo.category,
                'year': photo.date_taken.year if photo.date_taken else None,
                'date_formatted': photo.date_taken.strftime('%d. %m. %Y') if photo.date_taken else '',
                'album_id': photo.album.id if photo.album else None,
                'album_title': photo.album.title if photo.album else '',
                # --- NOVÉ ---
                'tags': photo.tags if photo.tags else ''
            })
            
    photos_json = json.dumps(map_data)

    return render(request, 'galerie/photo_list.html', {
        'photos': photos,
        'photos_json': photos_json,
        'available_years': available_years,
        'albums': albums  # --- NOVÉ: Posíláme alba do šablony ---
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
            messages.success(request, 'Photo was successfully uploaded!')
            return redirect('galerie:photo_list')  # After success, redirect back to the map
    else:
        form = PhotoUploadForm()  # If user just opened the page, show an empty form

    return render(request, 'galerie/upload.html', {'form': form})

# 1. Zobrazení tabulky všech fotek
@login_required
def manage_photos(request):
    photos = Photo.objects.all().order_by('-timestamp')
    
    # --- STATISTIKY PRO DASHBOARD ---
    total_photos = photos.count()
    photos_with_gps = photos.exclude(latitude__isnull=True).exclude(longitude__isnull=True).count()
    
    # Výpočet procent (bezpečné dělení nulou)
    gps_percentage = int((photos_with_gps / total_photos * 100)) if total_photos > 0 else 0
    
    # Spočítá, kolik fotek je v jaké kategorii
    category_stats = photos.values('category').annotate(count=Count('category')).order_by('-count')
    
    context = {
        'photos': photos,
        'total_photos': total_photos,
        'gps_percentage': gps_percentage,
        'category_stats': category_stats,
        'total_albums': Album.objects.count(),
    }
    return render(request, 'galerie/manage_photos.html', context)

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
            messages.success(request, 'Changes saved successfully!')
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
        messages.success(request, 'Photo was permanently deleted.')
        return redirect('galerie:manage_photos')
    
    # Pokud se sem dostane bez POST metody, ukážeme mu potvrzovací stránku
    return render(request, 'galerie/confirm_delete.html', {'photo': photo})

@login_required
def export_photos_zip(request):
    """Vytvoří ZIP soubor se všemi fotkami na pozadí a stáhne ho do PC"""
    photos = Photo.objects.exclude(image='') # Jen fotky, které mají soubor
    
    # Vytvoříme ZIP soubor v paměti RAM (nezatěžujeme pevný disk serveru)
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for photo in photos:
            try:
                # Otevřeme obrázek z URL (funguje pro lokál i Cloudinary)
                response = urllib.request.urlopen(photo.image.url)
                image_data = response.read()
                
                # Jméno souboru v ZIPu (např. "2023-Skotsko.webp")
                file_name = f"{photo.title.replace(' ', '_')}_{photo.pk}.webp"
                zip_file.writestr(file_name, image_data)
            except Exception as e:
                print(f"Chyba při stahování fotky {photo.title}: {e}")
                continue

    # Připravíme HTTP odpověď pro prohlížeč (spustí se stahování)
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="Scottish_Gallery_Backup.zip"'
    return response

@login_required
def bulk_upload(request):
    # Vytáhneme všechna existující alba pro výběr (seřazená od nejnovějšího)
    albums = Album.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        # Získáme seznam všech nahraných souborů
        files = request.FILES.getlist('photos')
        
        # Zjistíme, jestli uživatel vybral existující album, nebo vytvořil nové
        album_id = request.POST.get('album_id')
        new_album_name = request.POST.get('new_album_name')
        is_public = request.POST.get('is_public') == 'on'
        
        # Logika pro Album
        selected_album = None
        if new_album_name:
            # Vytvoříme zbrusu nové album
            selected_album = Album.objects.create(title=new_album_name)
        elif album_id:
            # Použijeme existující
            selected_album = get_object_or_404(Album, id=album_id)
            
        success_count = 0
        
        # Projdeme všechny nahrané soubory a vytvoříme pro ně záznamy
        for f in files:
            # Jako dočasný název fotky použijeme jméno souboru bez přípony (např. "IMG_1234")
            title = f.name.rsplit('.', 1)[0]
            
            photo = Photo(
                title=title,
                image=f,
                is_public=is_public,
                album=selected_album
            )
            photo.save() # Zde se spustí i naše chytrá komprese a EXIF logika!
            success_count += 1
            
        messages.success(request, f'Boom! {success_count} photos successfully uploaded and processed.')
        return redirect('galerie:manage_photos')
        
    return render(request, 'galerie/bulk_upload.html', {'albums': albums})