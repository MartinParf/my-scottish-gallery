# 1. Jaký operační systém a jazyk chceme? (Stáhne čistý Linux s Pythonem 3.12)
FROM python:3.12-slim

# 2. Nastavíme pracovní složku uvnitř kontejneru na /app
WORKDIR /app

# 3. Nastavení Pythonu, aby běžel rychleji a vypisoval logy rovnou na obrazovku
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 4. Zkopírujeme náš seznam knihoven a nainstalujeme je
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Zkopírujeme úplně zbytek našeho projektu do kontejneru
COPY . .

# 6. Řekneme Djangu, ať připraví CSS a JS soubory pro produkci (WhiteNoise)
RUN python manage.py collectstatic --noinput

# 7. Otevřeme pomyslné dveře na portu 8000
EXPOSE 8000

# 8. Startovací příkaz! Místo "runserver" použijeme produkční Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "skotsko_mapa.wsgi:application"]