import math
import numpy as np
import os
import platform

from qgis.core import QgsMessageLog

# Mix de https://github.com/tkrajina/srtm.py et https://github.com/aatishnn/srtm-python

HGT_DIR = "path/to/SRTM_HGT"

SAMPLES = 1201  # SRTM3

hgt_data = {}


def get_srtm_elevation(lon, lat):
    east_west = 'E' if lon >= 0 else 'W'
    north_south = 'N' if lat >= 0 else 'S'

    hgt_file_name = "{}{}{}{}.hgt".format(north_south, str(int(abs(math.floor(lat)))).zfill(2),
                                          east_west, str(int(abs(math.floor(lon)))).zfill(3))
    hgt_file_path = os.path.join(HGT_DIR, hgt_file_name)

    if hgt_file_name in hgt_data:
        elevations = hgt_data[hgt_file_name]
    elif os.path.isfile(hgt_file_path):
        with open(hgt_file_path, "rb") as data:
            elevations = np.fromfile(
                data,  # binary data
                np.dtype(">i2"),  # HGT is 16bit signed integer (i2) - big endian (>)
                SAMPLES * SAMPLES  # length
            ).reshape((SAMPLES, SAMPLES))
            hgt_data[hgt_file_name] = elevations
    else:
        QgsMessageLog.logMessage("(Plugin MNT) Fichier d'élévation manquant : " + hgt_file_path)
        return -32768

    lat_row = int(round((lat - int(lat)) * (SAMPLES - 1), 0))
    lon_row = int(round((lon - int(lon)) * (SAMPLES - 1), 0))

    if lat_row < 0:
        lat_row = abs(lat_row)
    else:
        lat_row = SAMPLES - 1 - lat_row

    return elevations[lat_row, lon_row].astype(int).item()


# if __name__ == '__main__':
#     HGT_DIR = "tot/toto/toto/toto.py"
#     # HGT_DIR = "\\\\freenas\\QGIS\\QGIS\\SRTM3"
#     print(os.path.abspath(HGT_DIR))
#     file = "toto.hgt"
#     print(os.path.join(HGT_DIR, file))
