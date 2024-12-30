import pandas as pd
import math
from datetime import datetime, timezone
from .classMNT import Mnt


class Point:
    def __init__(self, longitude, latitude, altitude,  tTS_ms, cap, assiette):
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude
        self.tTS_ms = tTS_ms
        self.cap = cap
        self.assiette = assiette
        self.azimuth , self.hauteur = self.get_azimut_hauteur()
        
    
    def get_longitude(self):
        return self.longitude
    def get_latitude(self):
        return self.latitude
    def get_altitude(self):
        return self.altitude
    def get_tTS_ms(self):
        return self.tTS_ms
    def get_cap(self):
        return self.cap
    def get_assiette(self):
        return self.assiette
    def get_azimut(self):
        return self.azimuth
    def get_hauteur(self):
        return self.hauteur
    
    
    def get_azimut_hauteur(self):
        # Récupération des attributs
        longitude = self.longitude
        latitude = self.latitude
        altitude = self.altitude
        tTS_ms = self.tTS_ms
        # Conversion du temps UNIX (ms) en datetime UTC
        time = tTS_ms / 1000
        dt_utc = datetime.fromtimestamp(time, tz=timezone.utc)
        # Calcul du jour
        jd = 2440587.5 + time / 86400
        # Calcul du nombre de siècles
        n = (jd - 2451545.0) / 36525.0
        # Calcul de la position du soleil
        # Longitude moyenne du soleil (en degrés)
        L = (280.46646 + n * (36000.76983 + n * 0.0003032)) % 360
        # Anomalie moyenne du soleil (en degrés)
        M = (357.52911 + n * (35999.05029 - 0.0001537 * n)) % 360
        # Excentricité de l'orbite terrestre
        e = 0.016708634 - n * (0.000042037 + 0.0000001267 * n)
        # Equation du centre (en degrés)
        C = (1.914602 - n * (0.004817 + 0.000014 * n)) * math.sin(math.radians(M)) \
            + (0.019993 - 0.000101 * n) * math.sin(math.radians(2 * M)) \
            + 0.000289 * math.sin(math.radians(3 * M))
        # Longitude vraie du soleil (en degrés)
        sun_true_long = L + C
        # Ascension droite (RA) et déclinaison (Dec)
        epsilon = 23.439292 - n * 0.0130042  # Inclinaison de l'axe terrestre
        sun_dec = math.degrees(math.asin(math.sin(math.radians(epsilon)) * math.sin(math.radians(sun_true_long))))
        sun_ra = math.degrees(math.atan2(math.cos(math.radians(epsilon)) * math.sin(math.radians(sun_true_long)),
                                         math.cos(math.radians(sun_true_long)))) % 360
        # Temps sidéral
        gmst = (280.46061837 + 360.98564736629 * (jd - 2451545.0) 
                + n**2 * (0.000387933 - n / 38710000.0)) % 360
        lmst = (gmst + longitude) % 360  # Temps sidéral local (en degrés)
        # Conversion en coordonnées horizontales
        ha = (lmst - sun_ra) % 360  # Angle horaire du soleil (en degrés)
        if ha > 180:
            ha -= 360  # Ajuster pour l'intervalle [-180, 180]
        ha_rad = math.radians(ha)
        dec_rad = math.radians(sun_dec)
        lat_rad = math.radians(latitude)
        # Hauteur
        hauteur_rad = math.asin(math.sin(lat_rad) * math.sin(dec_rad) +
                                 math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad))
        hauteur_deg = math.degrees(hauteur_rad)
        # Azimut
        azimuth_rad = math.atan2(-math.sin(ha_rad),
                                 math.tan(dec_rad) * math.cos(lat_rad) - math.sin(lat_rad) * math.cos(ha_rad))
        azimuth_deg = (math.degrees(azimuth_rad) + 360) % 360  # Convertir en degrés [0, 360]
        return azimuth_deg, hauteur_deg
        
    
    # def get_visibility(self,list_mnt_files_paths,mnt):
    #     longitude = math.radians(self.longitude)
    #     latitude = math.radians(self.latitude)
    #     altitude = self.altitude
    #     azimut = math.radians(self.get_azimut())
    #     hauteur = self.get_azimut_hauteur()
    #     R = 6371
    #     for distance in range(100):
    #         # Calcul de l'angle vertical entre les 2 points
    #         lat_mnt = math.asin(math.sin(latitude) * math.cos(distance / R) + math.cos(latitude) * math.sin(distance / R) * math.cos(azimut))
    #         lon_mnt = longitude + math.atan2(math.sin(azimut) * math.sin(distance / R) * math.cos(latitude), math.cos(distance / R) - math.sin(latitude) * math.sin(lat_mnt))
    #         mnt = Mnt()
    #         alt_mnt = mnt.getAltitude(lon_mnt,lat_mnt)
    #         delta_lat = lat_mnt - latitude
    #         delta_lon = lon_mnt - longitude  
    #         a = math.sin(delta_lat / 2)**2 + math.cos(latitude) * math.cos(lat_mnt) * math.sin(delta_lon / 2)**2
    #         c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    #         d_h = R * c 
    #         d_v = (alt_mnt - altitude) / 1000
    #         angle_rad = math.atan2(d_v, d_h)
    #         angle_deg = math.degrees(angle_rad)
    #         if angle_deg > hauteur:
    #             return False
    #     return True
    
    
    def get_estimation(self):
        pass
    
    