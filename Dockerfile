# 1. Choose base OS and language (pulls a minimal Linux image with Python 3.12)
FROM python:3.12-slim

# 2. Set the working directory inside the container to /app
WORKDIR /app

# 3. Configure Python for faster startup and unbuffered logging
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 4. Copy dependency list and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the project into the container
COPY . .

# 6. Ask Django to collect static files (CSS/JS) for production (served by WhiteNoise)
RUN python manage.py collectstatic --noinput

# 7. Expose port 8000
EXPOSE 8000

# 8. Startup command – use production-ready Gunicorn instead of "runserver"
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "skotsko_mapa.wsgi:application"]