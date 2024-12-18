import json
from qgis.core import QgsMessageLog, Qgis

import requests


def get_ign_elevations(lon_list, lat_list, url, query_type, resource, delimiter, max_size, json_key, task=None):
    lon_list = [str(lon) for lon in lon_list]
    lat_list = [str(lat) for lat in lat_list]

    elevations = []

    # https://geoservices.ign.fr/documentation/services/api-et-services-ogc/calcul-altimetrique-rest#1902
    # max_size = 5000
    for i in range(0, len(lon_list), max_size):
        if task:
            task.setProgress(i/(2*len(lon_list)))
        lon_chunk = lon_list[i:i + max_size]
        lat_chunk = lat_list[i:i + max_size]
        if query_type == "get":
            url = url.format(lon=delimiter.join(lon_chunk), lat=delimiter.join(lat_chunk))
            # QgsMessageLog.logMessage(f"MNT IGN url : {url}", 'Trajecto', level=Qgis.Info)
            response = requests.get(url)
            # QgsMessageLog.logMessage(f"MNT IGN response : {response}", 'Trajecto', level=Qgis.Info)
            elevations.extend(response.json()[json_key])
        elif query_type == "post":
            data = {"lon": delimiter.join(lon_chunk),
                    "lat": delimiter.join(lat_chunk),
                    "resource": resource,
                    "delimiter": delimiter,
                    "indent": "false",
                    "measures": "false",
                    "zonly": "true"}
            headers = {"accept": "application/json",
                       "Content-Type": "application/json"}
            response = requests.post(url=url, data=json.dumps(data), headers=headers)
            elevations.extend(response.json()[json_key])

    return elevations

