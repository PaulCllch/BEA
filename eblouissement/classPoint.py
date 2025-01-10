import numpy as np
import pandas as pd
import math
from datetime import datetime, timezone, timedelta
from .classMNT import Mnt


class Point:
    def __init__(self, longitude, latitude, altitude,  tTS_ms, cap, assiette, mnt_folder):
        self.mnt_folder = mnt_folder
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude
        self.tTS_ms = tTS_ms
        self.cap = cap
        self.assiette = assiette
        self.azimuth , self.hauteur = self.get_azimut_hauteur()
        self.visibility = self.calcul_visibility()
        self.estimation = self.calcul_estimation_eblouissement()
        
    
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
    def get_visibility(self):
        return self.visibility
    def get_estimation(self):
        return self.estimation
    
    # def get_azimut_hauteur(self):
    #     # Récupération des données
    #     longitude = np.radians(self.longitude)  # Conversion en radians
    #     latitude = np.radians(self.latitude)    # Conversion en radians
    #     tTS_ms = self.tTS_ms                    # Temps Unix en ms
    #     # Conversion du temps Unix en datetime
    #     datetime_obj = datetime.utcfromtimestamp(tTS_ms / 1000.0)
    #     jour_julien = datetime_obj.toordinal() + 1721424.5
    #     # Constantes astronomiques
    #     T = (jour_julien - 2451545.0) / 36525.0  # Temps en siècles julien depuis J2000.0
    #     eps = np.radians(23.439 - 0.013 * T)     # Obliquité de l'écliptique en radians
    #     PE = np.radians(282.937 + 1.724 * T)    # Longitude du périhélie en radians
    #     # Calculs du Soleil
    #     N = jour_julien - 2451545.0             # Numéro du jour depuis J2000.0
    #     Lm = np.radians((N * 360 / 365.25) - 279.9)  # Longitude écliptique moyenne
    #     Mm = Lm - PE                            # Anomalie moyenne en radians
    #     Lv = Lm + np.radians(1.9146 * np.sin(Mm) + 0.02 * np.sin(2 * Mm))  # Longitude vraie
    #     delta = np.arcsin(np.sin(Lv) * np.sin(eps))  # Déclinaison du Soleil en radians
    #     # Temps et angle horaire
    #     E = -0.1576 * np.sin(2 * Lv) / np.cos(delta) + 0.1276 * np.sin(Mm) - 0.0008 * np.sin(2 * Mm)
    #     TP = 12 + np.degrees(longitude) / 15 + E    # Temps de passage au méridien en heures
    #     heure = datetime_obj.hour + datetime_obj.minute / 60 + datetime_obj.second / 3600
    #     H = np.radians((heure - TP) * 15)          # Angle horaire en radians
    #     # Hauteur et azimut
    #     h = np.arcsin(np.sin(latitude) * np.sin(delta) + np.cos(latitude) * np.cos(delta) * np.cos(H))
    #     A = np.arctan2(np.sin(H), (np.cos(H) * np.sin(latitude) - np.tan(delta) * np.cos(latitude)))
    #     # Conversion en degrés pour le retour
    #     return np.degrees(A) % 360, np.degrees(h)
    
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
        
    
    def calcul_visibility(self):
        # Récupération des variables servant à déterminer des points sur la direction point soleil
        mnt_folder = self.mnt_folder
        lon_deg = self.longitude
        lat_deg = self.latitude
        # print(lon_deg,lat_deg)
        lon_rad = math.radians(lon_deg)
        lat_rad = math.radians(lat_deg)
        azimut = math.radians(self.get_azimut())
        # Récupération des variables qui permettent la comparaison entre les angles verticaux
        altitude = self.altitude
        hauteur = self.get_hauteur()
        # Rayon de la Terre
        R = 6371
        # Prise en compte de la dépression de l'horizon et de la réfraction atmosphérique
        h_km = altitude / 1000
        depression_horizon = math.degrees(math.sqrt(2 * h_km / R))
        refraction_correction = 1.02 / math.tan(math.radians(hauteur) + 10.3 / (hauteur + 5.11))
        hauteur = hauteur + refraction_correction - depression_horizon
        # Chargement de la première dalle utile
        val_N = np.floor(lat_deg)
        val_E = np.floor(lon_deg)
        mnt_file_name = 'N' + str(int(val_N)) + 'E' + str(int(val_E)).zfill(3) + '.hgt'
        mnt_path = str(mnt_folder) + '/' + str(mnt_file_name)
        mnt = Mnt(mnt_path,resolution=3)        
        for distance in range(20):
            # Longitude et latitude d'un point sur la direction point de la trajectoire soleil
            lat_mnt_rad = math.asin(math.sin(lat_rad) * math.cos(distance / R) + math.cos(lat_rad) * math.sin(distance / R) * math.cos(azimut))
            lon_mnt_rad = lon_rad + math.atan2(math.sin(azimut) * math.sin(distance / R) * math.cos(lat_rad), math.cos(distance / R) - math.sin(lat_rad) * math.sin(lat_mnt_rad))
            lat_mnt_deg = math.degrees(lat_mnt_rad)
            lon_mnt_deg = math.degrees(lon_mnt_rad)
            # Chargement d'une nouvelle dalle si besoin
            new_val_N, new_val_E = int(np.floor(lat_mnt_deg)), int(np.floor(lon_mnt_deg))
            if new_val_N != val_N or new_val_E != val_E:
                val_N, val_E = new_val_N, new_val_E
                mnt_file_name =  'N' + str(int(val_N)) + 'E' + str(int(val_E)).zfill(3) + '.hgt'
                mnt_path = str(mnt_folder) + '/' + str(mnt_file_name)
                mnt = Mnt(mnt_path, resolution=3) 
            # Détermination de l'altitude de ce point
            alt_mnt = mnt.getAltitude(lat_mnt_deg,lon_mnt_deg)
            # Calcul de l'angle vertical
            delta_lat = lat_mnt_deg - lat_deg
            delta_lon = lon_mnt_deg - lon_deg 
            a = math.sin(delta_lat / 2)**2 + math.cos(lat_deg) * math.cos(lat_mnt_deg) * math.sin(delta_lon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            d_h = R * c 
            d_v = (alt_mnt - altitude) / 1000
            angle_rad = math.atan2(d_v, d_h)
            angle_deg = math.degrees(angle_rad)
            # Si un des points déterminé à un angle vertical supérieur à l'élévation le soleil est caché
            if angle_deg > hauteur:
                return False
        # Sinon, le soleil est visible
        return True
    
    
    def calcul_estimation_eblouissement(self):
        # Pas d'éblouissement si le soleil n'est pas visible
        if not self.visibility:
            return 0 
        # Différence d'angle horizontale (en degrés)
        cap = self.cap
        azimut = self.azimuth
        diff_angle_horizontale = np.abs(cap - azimut) % 360
        if diff_angle_horizontale > 180:
            diff_angle_horizontale = 360 - diff_angle_horizontale
        # Estimation horizontale
        estimation_horizontale = max(0, 1 - (diff_angle_horizontale / 180)**2)
        # Différence d'angle verticale (en degrés)
        assiette = self.assiette
        hauteur = self.hauteur
        diff_angle_verticale = np.abs(assiette - hauteur)
        if diff_angle_verticale > 90:
            diff_angle_verticale = 90
        # Estimation verticale
        estimation_verticale = max(0, 1 - (diff_angle_verticale / 90)**2)
        # Combinaison des estimations avec pondération
        estimation = (0.7 * estimation_horizontale + 0.3 * estimation_verticale) * 100
    
        return estimation

    
    