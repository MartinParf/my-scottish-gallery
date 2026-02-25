from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from .utils import get_decimal_coordinates # Import naší nové funkce


CATEGORY_CHOICES = [
    ('nature', '🌲 Příroda a krajina'),
    ('architecture', '🏰 Architektura a města'),
    ('animals', '🐾 Zvířata'),
    ('people', '❤️ Lidé a momentky'),
    ('fun', '🍻 Zábava a relax'),
]


class Photo(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='photos/')
    description = models.TextField(blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    date_taken = models.DateTimeField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False, verbose_name="Veřejná fotka")
    tagged_people = models.ManyToManyField(User, blank=True, related_name="photos_of_me")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='nature', verbose_name="Kategorie")

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        
        # CHYTRÝ TRIK: Provedeme kompresi a čtení EXIFu jen u fotek, 
        # které ještě nejsou ve formátu WebP. Tím zabráníme tomu, aby se 
        # fotka komprimovala znovu a znovu, když v adminu jen změníte text u fotky.
        if self.image and not self.image.name.endswith('.webp'):
            
            # 1. Otevřeme obrázek v paměti pomocí Pillow
            img = Image.open(self.image)
            
            # 2. Vytáhneme EXIF data (pokud existují) a zkusíme najít GPS
            exif = img.getexif()
            if exif:
                # 2. Zkusíme najít GPS pomocí naší funkce
                lat, lon = get_decimal_coordinates(img)
                # Pokud jsme našli souřadnice a uživatel je nezadal ručně, doplníme je
                if lat and lon and not self.latitude and not self.longitude:
                    self.latitude = lat
                    self.longitude = lon
                    
            # 3. Změna velikosti (Moderní standard pro web)
            # Pokud je fotka větší než 1920 pixelů, zmenšíme ji
            output_size = (1920, 1920)
            img.thumbnail(output_size, Image.Resampling.LANCZOS)
            
            # 4. Komprese do formátu WebP
            output_buffer = BytesIO()
            # Uložíme obrázek do bufferu v paměti (kvalita 80% je vizuálně k nerozeznání od originálu)
            img.save(output_buffer, format='WEBP', quality=80)
            
            # 5. Nahradíme původní obří soubor tímto novým z bufferu
            # Změníme i příponu jména souboru na .webp
            new_file_name = f"{self.image.name.split('.')[0]}.webp"
            self.image.save(new_file_name, ContentFile(output_buffer.getvalue()), save=False)

        # Nakonec zavoláme původní ukládací metodu Djanga, aby se vše zapsalo do databáze
        super().save(*args, **kwargs)


@receiver(pre_delete, sender=Photo)
def delete_photo_from_cloudinary(sender, instance, **kwargs):
    """Při smazání fotky z DB smaže i soubor z Cloudinary (včetně hromadného mazání v adminu)."""
    if instance.image:
        try:
            instance.image.storage.delete(instance.image.name)
        except Exception:
            pass  # Aby výpadek sítě nebo chyba API neshodily celou aplikaci