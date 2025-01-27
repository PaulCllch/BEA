import numpy as np
import pandas as pd
import math
import os.path
import json
from datetime import datetime, timezone, timedelta
from .classMNT import Mnt
from .ign import get_ign_elevations

class Point:
    def __init__(self, longitude, latitude, altitude,  tTS_ms, cap, assiette, mnt_folder, sr_layer, bool_france):
        self.mnt_folder = mnt_folder
        self.sr_layer = sr_layer
        self.bool_france = bool_france
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
    
    
    def get_azimut_hauteur(self):
        # Récupération des attributs
        longitude = self.longitude
        latitude = self.latitude
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
        # Dans le cas ou on se situe en France et que l'utilisateur veut les MNT de l'IGN
        if self.bool_france:
            lon_list = []
            lat_list = []
            for d in range(500):
                distance = d*0.1
                # Longitude et latitude d'un point sur la direction point de la trajectoire soleil
                lat_mnt_rad = math.asin(math.sin(lat_rad) * math.cos(distance / R) + math.cos(lat_rad) * math.sin(distance / R) * math.cos(azimut))
                lon_mnt_rad = lon_rad + math.atan2(math.sin(azimut) * math.sin(distance / R) * math.cos(lat_rad), math.cos(distance / R) - math.sin(lat_rad) * math.sin(lat_mnt_rad))
                lat_mnt_deg = math.degrees(lat_mnt_rad)
                lon_mnt_deg = math.degrees(lon_mnt_rad)
                lon_list.append(lon_mnt_deg)
                lat_list.append(lat_mnt_deg)
            # Alttitudes des points sur la direction point de la trajectoire soleil
            geoservices_path = os.path.join(os.path.dirname(__file__), "geoservices.json")
            with open(geoservices_path, "r") as f:
                geoservices = json.load(f)
            url = geoservices["url_alti"]
            query_type = geoservices["query_type"]
            resource = geoservices["resource"]
            delimiter = geoservices["delimiter"]
            max_size = geoservices["max_query_number"]
            json_key = geoservices["json_key"]
            alt_list = get_ign_elevations(lon_list, lat_list, url, query_type, resource, delimiter, max_size, json_key)
            for k in range(len(alt_list)):
                # Calcul de l'angle vertical
                delta_lat = lat_list[k] - lat_deg
                delta_lon = lon_list[k] - lon_deg 
                a = math.sin(delta_lat / 2)**2 + math.cos(lat_deg) * math.cos(lat_mnt_deg) * math.sin(delta_lon / 2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                d_h = R * c 
                d_v = (alt_list[k] - altitude) / 1000
                angle_rad = math.atan2(d_v, d_h)
                angle_deg = math.degrees(angle_rad)
                if angle_deg > hauteur:
                    return False
        # Dans le cas ou nous somme à l'étranger et que l'utilisateur a renseigner un dossier contenant des fichiers hgt
        else:           
            # Chargement de la première dalle utile
            east_west = 'E' if lon_deg >= 0 else 'W'
            north_south = 'N' if lat_deg >= 0 else 'S'
            mnt_file_name1 = "{}{}{}{}.hgt".format(north_south, str(int(abs(math.floor(lat_deg)))).zfill(2),
                                                  east_west, str(int(abs(math.floor(lon_deg)))).zfill(3))
            mnt_path = str(mnt_folder) + '/' + str(mnt_file_name1)
            mnt = Mnt(mnt_path,resolution=3)        
            for d in range(1000):
                distance = d*0.1
                # Longitude et latitude d'un point sur la direction point de la trajectoire soleil
                lat_mnt_rad = math.asin(math.sin(lat_rad) * math.cos(distance / R) + math.cos(lat_rad) * math.sin(distance / R) * math.cos(azimut))
                lon_mnt_rad = lon_rad + math.atan2(math.sin(azimut) * math.sin(distance / R) * math.cos(lat_rad), math.cos(distance / R) - math.sin(lat_rad) * math.sin(lat_mnt_rad))
                lat_mnt_deg = math.degrees(lat_mnt_rad)
                lon_mnt_deg = math.degrees(lon_mnt_rad)
                # Chargement d'une nouvelle dalle si besoin
                east_west = 'E' if lon_mnt_deg >= 0 else 'W'
                north_south = 'N' if lat_mnt_deg >= 0 else 'S'
                mnt_file_name2 = "{}{}{}{}.hgt".format(north_south, str(int(abs(math.floor(lat_mnt_deg)))).zfill(2),
                                                      east_west, str(int(abs(math.floor(lon_mnt_deg)))).zfill(3))
                if mnt_file_name2 != mnt_file_name1:
                    mnt_file_name1 =  mnt_file_name2
                    mnt_path = str(mnt_folder) + '/' + str(mnt_file_name1)
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
        lon = self.longitude
        lat = self.latitude
        time = self.tTS_ms
        az = self.get_azimut()
        cap = self.cap
        azimut = self.azimuth
        diff_angle_horizontale = cap-azimut
        estimation_horizontale = np.exp(-0.001*diff_angle_horizontale**2)
        assiette = self.assiette
        hauteur = self.hauteur
        diff_angle_verticale = assiette-hauteur
        estimation_verticale = np.exp(-0.00035*diff_angle_verticale**2)
        # sr_layer = self.sr_layer
        # pts_reflecto = self.getIntersect(lon,lat,azimut,sr_layer)
        
        #     sr = SR(sr_folder)
        #     pts_reflect = sr.Intersect(lon,lat,az)
        #     for pt_reflect in pts_reflect:
        #         pt_reflect = Point(longitude, latitude, altitude, tTS_ms, cap, assiette, mnt_folder, sr_folder)
        #         h_pt_sun = pt_reflect.get_azimut()
        #         h_pt_avion = 
        #         if np.abs(h_pt_sun-h_pt-_avion)<5:
        #             estimation_verticale_sr =  np.exp(-0.00035*diff_angle_verticale_sr**2)
        #         if estimation_verticale_sr > estimation_verticale:
        #             estimation_verticale = estimation_verticale_sr
                    
        # Combinaison des estimations avec pondération
        estimation = ((estimation_horizontale)**2 * estimation_verticale) * 100
        return estimation

    # def getIntersect(self,lon,lat,azimut,mnt_folder,sr_layer):
    #     pts_reflecto = []
    #     lon_rad = math.radians(lon)
    #     lat_rad = math.radians(lat)
    #     R = 6371
    #     for distance in range(20):
    #         # Longitude et latitude d'un point sur la direction point de la trajectoire soleil
    #         lat_r_rad = math.asin(math.sin(lat_rad) * math.cos(distance / R) + math.cos(lat_rad) * math.sin(distance / R) * math.cos(azimut))
    #         lon_r_rad = lon_rad + math.atan2(math.sin(azimut) * math.sin(distance / R) * math.cos(lat_rad), math.cos(distance / R) - math.sin(lat_rad) * math.sin(lat_r_rad))
    #         lat_r_deg = math.degrees(lat_r_rad)
    #         lon_r_deg = math.degrees(lon_r_rad)
    #         # test si lat_r_deg et lon_r_deg
    #         pts_reflecto.append(lon_r_deg,lat_r_geh,alt_r)
    #     return pts_reflecto
        
        