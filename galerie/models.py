from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from .utils import get_decimal_coordinates  # Import our helper function
from datetime import datetime


CATEGORY_CHOICES = [
    ('nature', '🌲 Nature'),
    ('architecture', '🏰 Architecture'),
    ('animals', '🐾 Animals'),
    ('people', '❤️ People'),
    ('fun', '🍻 Fun'),
]

class Album(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_date = models.DateField(blank=True, null=True, help_text="Kdy výlet začal")
    end_date = models.DateField(blank=True, null=True, help_text="Kdy výlet skončil")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Photo(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='photos/', max_length=255)
    description = models.TextField(blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    date_taken = models.DateTimeField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False, verbose_name="Public Photo")
    tagged_people = models.ManyToManyField(User, blank=True, related_name="photos_of_me")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='nature', verbose_name="Category")
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True, related_name='photos', verbose_name="Album")

    tags = models.CharField(max_length=255, blank=True, help_text="AI or manual tags separated by comma")
    
    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):

        # SMART TRICK: We only compress and read EXIF data for photos
        # that are not yet in WebP format. This prevents the image from being
        # recompressed again and again when you only change text in the admin.
        if self.image and not self.image.name.endswith('.webp'):
            
            # 1. Open the image in memory using Pillow
            img = Image.open(self.image)
            
            # 2. Extract EXIF data (if present) and try to find GPS
            exif = img.getexif()
            if exif:
                # 2. Try to find GPS using our helper
                lat, lon = get_decimal_coordinates(img)
                # If we found coordinates and the user did not enter them manually, fill them in
                if lat and lon and not self.latitude and not self.longitude:
                    self.latitude = lat
                    self.longitude = lon
                # --- B. Extrakce Času pořízení (Vylepšená verze) ---
                if not self.date_taken:
                    date_str = exif.get(36867) or exif.get(306)  # Zkusí DateTimeOriginal nebo obyčejné DateTime
                    
                    # Pillow občas schovává data do podsekce (ExifOffset)
                    if not date_str:
                        try:
                            exif_ifd = exif.get_ifd(0x8769)
                            date_str = exif_ifd.get(36867)
                        except Exception:
                            pass
                            
                    if date_str:
                        try:
                            self.date_taken = datetime.strptime(str(date_str).strip(), '%Y:%m:%d %H:%M:%S')
                        except Exception:
                            pass     

            # 3. Resize (modern web standard)
            # If the photo is larger than 1920 pixels, downscale it
            output_size = (1920, 1920)
            img.thumbnail(output_size, Image.Resampling.LANCZOS)
            
            # 4. Compress to WebP
            output_buffer = BytesIO()
            # Save the image into an in‑memory buffer (quality 80% is visually almost indistinguishable)
            img.save(output_buffer, format='WEBP', quality=80)
            
            # 5. Replace the original large file with this new one from the buffer
            # Also change the file extension to .webp
            new_file_name = f"{self.image.name.split('.')[0]}.webp"
            self.image.save(new_file_name, ContentFile(output_buffer.getvalue()), save=False)

        # Finally call Django's original save method so everything is written to the database
        super().save(*args, **kwargs)


@receiver(pre_delete, sender=Photo)
def delete_photo_from_cloudinary(sender, instance, **kwargs):
    """When a photo is deleted from the DB, also delete the file from Cloudinary (including bulk deletes from the admin)."""
    if instance.image:
        try:
            instance.image.storage.delete(instance.image.name)
        except Exception:
            pass  # Ensure a network outage or API error does not crash the application