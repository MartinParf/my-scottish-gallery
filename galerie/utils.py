from PIL import Image, ExifTags

def get_decimal_coordinates(img):
    """
    Vezme otevřený obrázek (Pillow Image), najde v něm GPS tagy 
    a přepočítá je ze Stupňů/Minut/Vteřin na desetinné číslo pro mapu.
    """
    try:
        exif = img.getexif()
        if not exif:
            return None, None
            
        # V moderním Pillow se GPS data schovávají ve speciální sekci (tag 34853)
        gps_ifd = exif.get_ifd(ExifTags.Base.GPSInfo)
        if not gps_ifd:
            return None, None
        
        # Přeložíme číselné kódy na lidské názvy (např. 2 -> 'GPSLatitude')
        gps_info = {}
        for key, val in gps_ifd.items():
            tag_name = ExifTags.GPSTAGS.get(key, key)
            gps_info[tag_name] = val
            
        # Vytáhneme konkrétní data pro výpočet
        lat = gps_info.get('GPSLatitude')
        lat_ref = gps_info.get('GPSLatitudeRef')
        lon = gps_info.get('GPSLongitude')
        lon_ref = gps_info.get('GPSLongitudeRef')
        
        if not (lat and lat_ref and lon and lon_ref):
            return None, None
            
        # Přepočet DMS na desetinné číslo
        # (float(X[0]) jsou Stupně, float(X[1])/60 jsou Minuty, float(X[2])/3600 jsou Vteřiny)
        lat_decimal = float(lat[0]) + (float(lat[1]) / 60.0) + (float(lat[2]) / 3600.0)
        lon_decimal = float(lon[0]) + (float(lon[1]) / 60.0) + (float(lon[2]) / 3600.0)
        
        # Pokud je to na Jih (S) nebo Západ (W), souřadnice musí být záporná!
        # Skotsko je na Západ (W) od nultého poledníku, takže longitude bude záporné číslo.
        if lat_ref == 'S':
            lat_decimal = -lat_decimal
        if lon_ref == 'W':
            lon_decimal = -lon_decimal
            
        # Zaokrouhlíme na 6 desetinných míst (pro Leaflet mapy je to přesnost na centimetry)
        return round(lat_decimal, 6), round(lon_decimal, 6)
        
    except Exception as e:
        # Pokud se něco pokazí, vytiskne se chyba do terminálu a program jede dál
        print(f"Nepodařilo se přečíst GPS: {e}")
        return None, None