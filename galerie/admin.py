from django.contrib import admin

from .models import Photo


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'timestamp', 'date_taken', 'latitude', 'longitude')
    list_filter = ('category',)
