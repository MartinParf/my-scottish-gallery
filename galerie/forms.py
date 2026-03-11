from django import forms
from .models import Photo

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'image', 'description', 'is_public', 'category', 'latitude', 'longitude']
        
        # Add CSS classes for a modern look so the form does not feel outdated
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Photo title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

class PhotoEditForm(forms.ModelForm):
    class Meta:
        model = Photo
        # Všimněte si, že tu CHYBÍ pole 'image'. To chrání originální fotku.
        fields = ['title', 'description', 'category', 'is_public', 'latitude', 'longitude', 'date_taken']
        
        # HTML widget pro hezký výběr data a času
        widgets = {
            'date_taken': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }