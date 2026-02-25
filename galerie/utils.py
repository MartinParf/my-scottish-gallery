from PIL import Image, ExifTags

def get_decimal_coordinates(img):
    """
    Take an opened Pillow Image, find GPS tags
    and convert them from Degrees/Minutes/Seconds to a decimal value for the map.
    """
    try:
        exif = img.getexif()
        if not exif:
            return None, None
            
        # In modern Pillow, GPS data are stored in a special section (tag 34853)
        gps_ifd = exif.get_ifd(ExifTags.Base.GPSInfo)
        if not gps_ifd:
            return None, None
        
        # Translate numeric codes into human-readable names (e.g. 2 -> 'GPSLatitude')
        gps_info = {}
        for key, val in gps_ifd.items():
            tag_name = ExifTags.GPSTAGS.get(key, key)
            gps_info[tag_name] = val
            
        # Extract the specific data we need for the calculation
        lat = gps_info.get('GPSLatitude')
        lat_ref = gps_info.get('GPSLatitudeRef')
        lon = gps_info.get('GPSLongitude')
        lon_ref = gps_info.get('GPSLongitudeRef')
        
        if not (lat and lat_ref and lon and lon_ref):
            return None, None
            
        # Convert DMS to decimal value
        # (float(X[0]) are Degrees, float(X[1])/60 are Minutes, float(X[2])/3600 are Seconds)
        lat_decimal = float(lat[0]) + (float(lat[1]) / 60.0) + (float(lat[2]) / 3600.0)
        lon_decimal = float(lon[0]) + (float(lon[1]) / 60.0) + (float(lon[2]) / 3600.0)
        
        # If the reference is South (S) or West (W), the coordinate must be negative.
        # Scotland is West (W) of the prime meridian, so longitude will be a negative number.
        if lat_ref == 'S':
            lat_decimal = -lat_decimal
        if lon_ref == 'W':
            lon_decimal = -lon_decimal
            
        # Round to 6 decimal places (for Leaflet maps this is centimeter‑level precision)
        return round(lat_decimal, 6), round(lon_decimal, 6)
        
    except Exception as e:
        # If something goes wrong, print the error to the console and continue
        print(f"Failed to read GPS data: {e}")
        return None, None