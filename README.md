# Scottish Photo Gallery & Map

Interactive photo gallery focused on Scotland, combining beautiful user-uploaded images with a map-based exploration experience.

## Live Demo

[Live Website](https://my-scottish-gallery.fly.dev/)

## Key Features

- **Interactive map view**: Explore photos directly on a map of Scotland, with clustered markers, custom category-based pins, and a lightbox viewer for full-size images and captions.
- **Photo upload with GPS support**: Upload photos from desktop or mobile; GPS coordinates are read from EXIF when available, or can be set manually via an embedded map and geocoding search.
- **Categories & privacy controls**: Assign each photo to a category (nature, architecture, animals, people, fun) and choose whether it is public or private.
- **Tagging people**: Tag registered users in photos so they can quickly find pictures they appear in.
- **Modern UI with light/dark mode**: Clean, responsive design with a global light/dark theme toggle; the map and UI automatically adapt to the selected mode.
- **Admin interface**: Full Django admin for managing photos, categories, and user-related data, including bulk operations that safely clean up stored media.

## Tech Stack

- **Backend**: Django (Python)
- **Database**: PostgreSQL (hosted on Supabase)
- **Media storage**: Cloudinary via Django storage backend for efficient image hosting, transformation, and CDN delivery
- **Frontend**:
  - Django templates
  - Leaflet.js + MarkerCluster for the interactive map
  - Modern responsive CSS (custom styles, mobile-optimized navigation, dark mode)
- **Deployment**: Fly.io (Docker-based deployment, environment-specific settings, WhiteNoise for static assets)

## Security

- **Secrets & configuration**: Sensitive values (e.g. `SECRET_KEY`, database URL, Cloudinary credentials) are never hard-coded; they are loaded from environment variables via `.env` in development and platform-provided env vars in production.
- **Authentication & authorization**: Built on Django's auth system, with a protected admin area and access-controlled photo visibility (public vs. private).
- **Database access**: PostgreSQL is accessed via secure connection parameters and does not expose a public, anonymous API endpoint.
- **CSRF & session protection**: Django's built-in CSRF protection and session management are enabled, with trusted origins configured for the deployed Fly.io domain.

