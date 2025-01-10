import numpy as np

class Mnt:
    def __init__(self, filepath, resolution=3):
        self.filepath = filepath
        self.resolution = resolution
        self.size = 3600 // resolution + 1
        self.data = self.loadHgtFile()
        self.coordinates = self.LonLatCoordinates()


    def loadHgtFile(self):
        """Charge les données d'altitude depuis le fichier .hgt."""
        try:
            with open(self.filepath, 'rb') as file:
                data = np.fromfile(file, dtype='>i2')  # '>i2' pour big-endian int16
                if data.size != self.size**2:
                    raise ValueError("Le fichier n'a pas la taille attendue pour la résolution spécifiée.")
                return data.reshape((self.size, self.size))
        except FileNotFoundError:
            raise FileNotFoundError(f"Le fichier {self.filepath} est introuvable.")
        except Exception as e:
            raise RuntimeError(f"Erreur lors du chargement du fichier : {e}")
            

    def LonLatCoordinates(self):
        """Calcule les coordonnées des points du MNT."""
        # Extraire la latitude et la longitude du nom de fichier
        filename = self.filepath.split('/')[-1]
        lat = int(filename[1:3]) * (1 if filename[0] == 'N' else -1)
        lon = int(filename[4:7]) * (1 if filename[3] == 'E' else -1)
        # Calculer les coordonnées
        latitudes = np.linspace(lat, lat + 1, self.size)
        longitudes = np.linspace(lon, lon + 1, self.size)
        return np.array(np.meshgrid(latitudes, longitudes)).T


    def getAltitude(self, lat, lon):
        """Récupère l'altitude pour une latitude et une longitude données."""
        # Déterminer les coordonnées minimales
        lat_min = self.coordinates[0, 0, 0]
        lon_min = self.coordinates[0, 0, 1]
        # Calculer les indices à partir de la latitude et longitude
        lat_idx = int((lat_min + 1 - lat) * (self.size - 1))  # Latitude décroissante dans les données
        lon_idx = int((lon - lon_min) * (self.size - 1))  # Longitude croissante dans les données
        # Vérifier si les indices sont dans les limites
        if 0 <= lat_idx < self.size and 0 <= lon_idx < self.size:
            return self.data[lat_idx, lon_idx]
        else:
            raise ValueError(f"Les coordonnées ({lat}, {lon}) sont en dehors des limites du MNT.")


