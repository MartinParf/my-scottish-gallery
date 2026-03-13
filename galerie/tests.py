from django.test import TestCase, override_settings
from django.urls import reverse

# Říkáme robotovi: Vypni Whitenoise a vypni i přesměrování na HTTPS!
@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}
    },
    SECURE_SSL_REDIRECT=False  # <--- TOTO JE TA ZÁCHRANA
)
class GallerySmokeTests(TestCase):
    def test_homepage_loads_successfully(self):
        """Test, zda hlavní mapa běží a nevrací Error 500"""
        response = self.client.get(reverse('galerie:photo_list'))
        self.assertEqual(response.status_code, 200)

    def test_photo_hub_is_protected(self):
        """Test, zda je Photo Hub chráněn před nepřihlášenými uživateli"""
        response = self.client.get(reverse('galerie:manage_photos'))
        self.assertEqual(response.status_code, 302)