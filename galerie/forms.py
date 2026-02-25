from django import forms
from .models import Photo

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'image', 'description', 'is_public', 'category', 'latitude', 'longitude']
        
        # Přidáme CSS třídy pro náš moderní vzhled, aby formulář nevypadal jako z roku 1995
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Název fotky'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }