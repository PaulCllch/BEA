import pandas as pd
import numpy as np

from .classPoint import Point

class Trajectoire:
    def __init__(self, df_pts, mnt_folder,sr_layer,bool_france):
        self.df_pts = df_pts
        self.mnt_folder = mnt_folder
        self.sr_layer = sr_layer
        self.bool_france = bool_france
        self.list_pts = self.create_list_pts()
        self.df_pts_maj = self.maj_df_pts()
        self.bool_france = bool_france
        
        
    def get_df_pts(self):
        return self.df_pts
    def get_mnt_folder(self):
        return self.mnt_folder
    def get_sr_layer(self):
        return self.sr_layer
    def get_list_pts(self):
        return self.list_pts
    def get_df_pts_maj(self):
        return self.df_pts_maj
    

    def create_list_pts(self):
        print("Calcul des champs aimut, hauteur, visibilité et éblouissement en cours...")
        list_pts = []
        df_pts = self.get_df_pts()
        nb_pts = len(df_pts)
        for pt in range(nb_pts):
            longitude = df_pts.at[pt, 'longitude']
            latitude = df_pts.at[pt, 'latitude']
            altitude = df_pts.at[pt, 'altitude']
            tTS_ms = df_pts.at[pt, 'tTS_ms']
            cap = df_pts.at[pt, 'cap']
            assiette = df_pts.at[pt, 'assiette']
            point = Point(longitude, latitude, altitude, tTS_ms, cap, assiette, self.mnt_folder, self.sr_layer, self.bool_france)
            list_pts.append(point)        
        return list_pts
    
    
    def maj_df_pts(self):
        list_pts = self.list_pts
        attributs = ['longitude', 'latitude', 'altitude', 'tTS_ms', 'cap', 'assiette','azimut_sun' ,'hauteur_sun','visibility','estimation']
        data = []
        for pt in list_pts:
            data.append([pt.get_longitude(),pt.get_latitude(),pt.get_altitude(),pt.get_tTS_ms(),pt.get_cap(),pt.get_assiette(),pt.get_azimut(),pt.get_hauteur(),pt.get_visibility(),pt.get_estimation()])
        df_pts_maj = pd.DataFrame(data ,columns=attributs)
        return df_pts_maj
        
        
    def emprise(self):
        df_pts = self.get_df_pts()
        lon_min, lon_max = df_pts['longitude'].min(), df_pts['longitude'].max()
        lat_min, lat_max = df_pts['latitude'].min(), df_pts['latitude'].max()
        emprise = np.array([[lon_min, lon_max],
                            [lat_min, lat_max]])
        return emprise

