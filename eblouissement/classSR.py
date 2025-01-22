import geopandas as gpd
from shapely.geometry import Point, LineString
import numpy as np

class SR:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = None
    
    def loadShpFile(self):
        """Charge le fichier shapefile à partir du chemin spécifié."""
        try:
            self.data = gpd.read_file(self.filepath)
            print(f"Fichier shapefile chargé avec succès : {self.filepath}")
        except Exception as e:
            print(f"Erreur lors du chargement du fichier shapefile : {e}")
    
    def intersect(self, lon, lat, az=None):
        """Vérifie si la demi-droite passant par un point (longitude, latitude) et
        ayant la direction de l'azimut intersecte une ou plusieurs entités du 
        shapefile et retourne une liste de points intersectés."""
        if self.data is None:
            print("Aucun fichier shapefile chargé. Veuillez d'abord charger un fichier.")
            return None
        point = Point(lon, lat)
        if az is None:
            # Vérifie l'intersection du point avec les entités du shapefile
            intersections = self.data[self.data.geometry.intersects(point)]
        else:
            # Crée une ligne basée sur l'azimut
            # Exemple simplifié : ligne partant du point (lon, lat) sur une courte distance
            line_length = 20  # longueur arbitraire
            end_lon = lon + line_length * np.cos(np.radians(az))
            end_lat = lat + line_length * np.sin(np.radians(az))
            line = LineString([(lon, lat), (end_lon, end_lat)])
            # Vérifie l'intersection de la ligne avec les entités du shapefile
            intersections.append([lon,lat])
        return intersections
