import pandas as pd
import numpy as np
from classPoint import Point

class Trajectoire:
    def __init__(self, cd):
        self.cd = cd
        self.df_pts = self.create_df_pts()
        self.list_pts = self.create_list_pts()
        
    def create_df_pts(self):
        cd = self.cd
        csv = pd.read_csv(cd,delimiter=";")
        attribus = ["id","longitude","latitude","alt_m","alt_ft","tTime_utc",
                    "tTS_ms","h_sec","h_UTC","tTime_loc","h_loc"]
        df_pts = csv[attribus]
        return df_pts
    
    def create_list_pts(self):
        df_pts = self.df_pts
        list_pts = []
        size = df_pts.shape
        nb_pts = size[0]
        for pt in nb_pts:
            id_pt = df_pts['id'].iloc[pt]
            longitude = df_pts['longitude'].iloc[pt]
            latitude = df_pts['latitude'].iloc[pt]
            alt_m = df_pts['alt_m'].iloc[pt]
            alt_ft = df_pts['alt_ft'].iloc[pt]
            tTime_utc = df_pts['tTime_utc'].iloc[pt]
            tTS_ms = df_pts['tTS_ms'].iloc[pt]
            h_sec = df_pts['h_sec'].iloc[pt]
            h_UTC = df_pts['h_UTC'].iloc[pt]
            tTime_loc = df_pts['tTime_loc'].iloc[pt]
            h_loc = df_pts['h_loc'].iloc[pt]
            point = Point(id_pt, longitude, latitude, alt_m, alt_ft, tTime_utc, tTS_ms, h_sec, h_UTC, tTime_loc, h_loc)
            list_pts.append(point)
        return list_pts