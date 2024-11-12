import pandas as pd
from astral import LocationInfo
from astral.sun import sun
from datetime import datetime

class Point:
    def __init__(self,id_pt,longitude,latitude,alt_m,alt_ft,tTime_utc,tTS_ms,h_sec,h_UTC,tTime_loc,h_loc):
        self.id_pt
        self.longitude
        self.latitude
        self.alt_m
        self.alt_ft
        self.tTime_utc
        self.tTS_ms
        self.h_sec
        self.h_UTC
        self.tTime_loc
        self.h_loc
        self.azimuth = self.get_azimuth()
        self.elevation = self.get_elevation()
        
        
    def get_id_pt(self):
        return self.id_pt
    def get_longitude(self):
        return self.longitude
    def get_latitude(self):
        return self.latitude
    def get_alt_m(self):
        return self.alt_m
    def get_alt_ft(self):
        return self.alt_ft
    def get_tTime_utc(self):
        return self.tTime_utc
    def tTS_ms(self):
        return self.tTS_ms
    def get_h_sec(self):
        return self.h_sec
    def get_h_UTC(self):
        return self.h_UTC
    def get_tTime_loc(self):
        return self.tTime_loc
    def get_h_loc(self):
        return self.h_loc
    
    def get_azimuth(self):
        latitude = self.latitude
        longitude = self.longitude
        location = LocationInfo(latitude,longitude)
        soleil = sun(location.observer, date=datetime.now(), tzinfo=location.timezone)
        azimuth = soleil['azimuth']
        return azimuth    
    
    def get_elevation(self):
        latitude = self.latitude
        longitude = self.longitude
        location = LocationInfo(latitude,longitude)
        soleil = sun(location.observer, date=datetime.now(), tzinfo=location.timezone)
        elevation = soleil['elevation']
        return elevation
    

    