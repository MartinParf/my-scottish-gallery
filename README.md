# 📸 Scottish Gallery

![Django](https://img.shields.io/badge/Django-6.0.2-092E20?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=Leaflet&logoColor=white)
![Cloudinary](https://img.shields.io/badge/Cloudinary-3448C5?style=for-the-badge&logo=Cloudinary&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Sentry](https://img.shields.io/badge/Sentry-362D59?style=for-the-badge&logo=sentry&logoColor=white)

**Scottish Gallery** is a modern, interactive map-based photo gallery showcasing our memories from Scotland. It features an interactive map for geographical context, a Pinterest-style masonry grid, automatic EXIF metadata extraction, and a dedicated Photo Hub for seamless image management.

🚀 **Live Demo:** [https://my-scottish-gallery.fly.dev](https://my-scottish-gallery.fly.dev)

---

## ✨ Key Features & Technical Highlights

* **Interactive Map & Gallery Views:** Seamlessly toggle between a CartoDB Leaflet map with clustered photo pins and a highly responsive masonry grid.
* **Smart Bulk Uploads:** Drag-and-drop multiple photos at once. The backend automatically extracts GPS coordinates and timestamps directly from EXIF data.
* **Album & Tag Management:** Group photos into albums and assign tags for quick filtering. Clicking a tag dynamically filters both the map and the gallery.
* **Advanced Filtering:** Multi-dimensional filtering by Category, Year, Album, and Tags without page reloads.
* **Analytics Dashboard:** A real-time Photo Hub displaying total photos, GPS coverage percentage, and top categories.
* **Instant ZIP Backup:** Package and download all hosted photos into a ZIP file entirely in memory.

## 🛠️ Tech Stack

* **Backend:** Django 6.x, Python 3.12
* **Database:** PostgreSQL
* **Static & Media:** Cloudinary (Media files) + WhiteNoise (Static files)
* **Frontend:** TailwindCSS, Vanilla JavaScript, HTML5, Leaflet.js
* **Monitoring:** Sentry SDK for real-time error and performance tracking.
* **Deployment:** Containerized and hosted on Fly.io (Gunicorn WSGI).

---

## 🚀 CI/CD Pipeline & Deployment

The deployment process is fully automated to ensure rapid and reliable updates. 
* **GitHub Actions:** A CI/CD workflow is configured to automatically trigger upon every `git push` to the `main` branch.
* **Code Validation & Testing:** Ruff Linter ensures code quality, while Django Unit Tests run in an isolated PostgreSQL container before every deployment.
* **Fly.io:** The application is containerized and continuously deployed to Fly.io.
* **Database Migrations:** Django migrations and static file collection (`collectstatic` via WhiteNoise) are handled automatically during the build phase.

This zero-downtime deployment strategy allows for seamless shipping of new features with a single git command.

---

## 🗺️ Roadmap & Future Enhancements

The gallery is a living project. Here are the planned features for upcoming releases:

- [ ] **Real-world Stress Testing:** Populate the database with 100+ high-resolution, Lightroom-processed images to test map clustering efficiency and masonry grid performance in production.
- [ ] **Progressive Web App (PWA):** Implement a `manifest.json` and Service Workers to allow users to install the gallery on their mobile devices for a native app-like experience.
- [ ] **AI-Powered Auto-Tagging (v2.0):** Integrate Hugging Face Vision API (or OpenAI) to automatically generate descriptive tags and captions for uploaded photos with a single "Magic Button" click.
- [ ] **Asynchronous Background Processing:** Introduce Celery and Redis to handle heavy lifting (like generating huge ZIP backups and processing massive bulk uploads) outside the main request-response cycle.

---
*Designed and built with ❤️ by Martin, Martina, and Olivia.*