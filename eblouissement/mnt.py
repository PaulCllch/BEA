import json
import os.path as op

from .ign import get_ign_elevations
from .srtm import get_srtm_elevation

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QVariant, QObject
from PyQt5.QtWidgets import QApplication, QAction, QDialogButtonBox

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsVectorDataProvider,
    QgsCoordinateReferenceSystem, QgsCoordinateTransform,
    QgsWkbTypes, QgsField, NULL, QgsMessageLog, Qgis
)

# cf https://api.qgis.org/api/3.16/classQgsVectorLayer.html#a9334033354a994132b28fcd1700b64e3
URL = "url_alti"
QUERY_TYPE = "query_type"
RESOURCE = "resource"
DELIMITER = "delimiter"
MAX_QUERY_NUMBER = "max_query_number"
JSON_KEY = "json_key"


class Mnt(QObject):

    def __init__(self):
        super().__init__()
        self.project = QgsProject.instance()
        self.first_start = None
        self.comboBoxLayers = []

    def create_fields(self, layer, fields):
        for field_name, field_type in fields:
            if layer.fields().indexFromName(field_name) == -1:
                layer.dataProvider().addAttributes([QgsField(field_name, field_type)])
                layer.updateFields()

    def compute_ign_elevations(self, layer):
        mnt_ign_m = layer.fields().indexFromName("mnt_ign_m")
        mnt_ign_ft = layer.fields().indexFromName("mnt_ign_ft")
        lon_list, lat_list = [], []
        for feature in layer.getFeatures():
            point = self.to4326.transform(feature.geometry().asPoint())
            lon_list.append(point.x())
            lat_list.append(point.y())

        ign_elevations = get_ign_elevations(lon_list, lat_list)

        nb_updated_points = 0
        for feature, elevation in zip(layer.getFeatures(), ign_elevations):
            if elevation != -99999:
                # feature["mnt_ign_m"] = elevation
                # feature["mnt_ign_ft"] = elevation * 3.28084
                layer.changeAttributeValue(feature.id(), mnt_ign_m, elevation)
                layer.changeAttributeValue(feature.id(), mnt_ign_ft, elevation * 3.28084)
                nb_updated_points += 1
            else:
                # feature["mnt_ign_m"] = NULL
                # feature["mnt_ign_ft"] = NULL
                layer.changeAttributeValue(feature.id(), mnt_ign_m, NULL)
                layer.changeAttributeValue(feature.id(), mnt_ign_ft, NULL)

            # layer.updateFeature(feature)

        return nb_updated_points

    def compute_srtm_elevations(self, layer):
        srtm_m = layer.fields().indexFromName("srtm_m")
        srtm_ft = layer.fields().indexFromName("srtm_ft")
        nb_updated_points = 0
        for feature in layer.getFeatures():
            point = self.to4326.transform(feature.geometry().asPoint())
            elevation = get_srtm_elevation(point.x(), point.y())

            if elevation != -32768:
                # feature["srtm_m"] = elevation
                # feature["srtm_ft"] = elevation * 3.28084
                layer.changeAttributeValue(feature.id(), srtm_m, elevation)
                layer.changeAttributeValue(feature.id(), srtm_ft, elevation * 3.28084)
                nb_updated_points += 1
            else:
                # feature["srtm_m"] = NULL
                # feature["srtm_ft"] = NULL
                layer.changeAttributeValue(feature.id(), srtm_m, NULL)
                layer.changeAttributeValue(feature.id(), srtm_ft, NULL)

            # layer.updateFeature(feature)

        return nb_updated_points

    def compute_ign_srtm_elevations(self, task, layer, nb_points, dlg=None, **kwargs):
        # mnt_m = layer.fields().indexFromName("mnt_m")
        # mnt_ft = layer.fields().indexFromName("mnt_ft")
        # mnt_source = layer.fields().indexFromName("mnt_source")
        # hauteur_m = layer.fields().indexFromName("hauteur_m")
        # hauteur_ft = layer.fields().indexFromName("hauteur_ft")

        lon_list, lat_list = [], []
        for feature in layer.getFeatures():
            to4326 = QgsCoordinateTransform(layer.sourceCrs(), QgsCoordinateReferenceSystem.fromEpsgId(4326),
                                            self.project)
            point = to4326.transform(feature.geometry().asPoint())
            lon_list.append(point.x())
            lat_list.append(point.y())

        local_geoservices = op.join(op.dirname(__file__), "geoservices.json")
        with open(local_geoservices) as file:
            geoservices = json.load(file)
            url = geoservices[URL]
            query_type = geoservices[QUERY_TYPE]
            resource = geoservices[RESOURCE]
            delimiter = geoservices[DELIMITER]
            max_req = geoservices[MAX_QUERY_NUMBER]
            json_key = geoservices[JSON_KEY]

        ign_elevations = get_ign_elevations(lon_list, lat_list, url=url, query_type=query_type, resource=resource,
                                            delimiter=delimiter, max_size=max_req, json_key=json_key)
        return {"layer": layer,
                "lon_list": lon_list,
                "lat_list": lat_list,
                "ign_elevations": ign_elevations,
                "nb_points": nb_points,
                "dlg": dlg}

    def write_elevations(self, exception, result=None):
        if exception is not None:
            QgsMessageLog.logMessage("Exception: {}".format(exception), "Trajecto", Qgis.Critical)
            raise exception

        layer = result["layer"]
        lon_list = result["lon_list"]
        lat_list = result["lat_list"]
        ign_elevations = result["ign_elevations"]
        nb_points = result["nb_points"]

        mnt_ign_m = layer.fields().indexFromName("mnt_ign_m")
        mnt_ign_ft = layer.fields().indexFromName("mnt_ign_ft")
        srtm_m = layer.fields().indexFromName("srtm_m")
        srtm_ft = layer.fields().indexFromName("srtm_ft")

        self.create_fields(layer, (("mnt_m", QVariant.Double),
                                   ("mnt_ft", QVariant.Double),
                                   ("mnt_source", QVariant.String),
                                   ("hauteur_m", QVariant.Double),
                                   ("hauteur_ft", QVariant.Double)))

        nb_updated_points_ign = 0
        nb_updated_points_srtm = 0
        i = 0
        length = len(list(zip(layer.getFeatures(), ign_elevations)))
        for feature, elevation in zip(layer.getFeatures(), ign_elevations):
            if elevation != -99999:
                feature["mnt_m"] = elevation
                feature["mnt_ft"] = elevation * 3.28084
                feature["mnt_source"] = "IGN"
                # layer.changeAttributeValue(feature.id(), mnt_m, elevation)
                # layer.changeAttributeValue(feature.id(), mnt_ft, elevation * 3.28084)
                # layer.changeAttributeValue(feature.id(), mnt_source, "IGN")
                if mnt_ign_m != -1 and mnt_ign_ft != -1:
                    feature["mnt_ign_m"] = elevation
                    feature["mnt_ign_ft"] = elevation * 3.28084
                    # layer.changeAttributeValue(feature.id(), mnt_ign_m, elevation)
                    # layer.changeAttributeValue(feature.id(), mnt_ign_ft, elevation * 3.28084)
                nb_updated_points_ign += 1
            else:
                srtm_elevation = get_srtm_elevation(lon_list[i], lat_list[i])
                if srtm_elevation != -32768:
                    feature["mnt_m"] = srtm_elevation
                    feature["mnt_ft"] = srtm_elevation * 3.28084
                    feature["mnt_source"] = "SRTM3"
                    # layer.changeAttributeValue(feature.id(), mnt_m, srtm_elevation)
                    # layer.changeAttributeValue(feature.id(), mnt_ft, srtm_elevation * 3.28084)
                    # layer.changeAttributeValue(feature.id(), mnt_source, "SRTM3")
                    if srtm_m != -1 and srtm_ft != -1:
                        feature["srtm_m"] = srtm_elevation
                        feature["srtm_ft"] = srtm_elevation * 3.28084
                        # layer.changeAttributeValue(feature.id(), srtm_m, elevation)
                        # layer.changeAttributeValue(feature.id(), srtm_ft, elevation * 3.28084)
                    nb_updated_points_srtm += 1
                else:
                    feature["mnt_m"] = NULL
                    feature["mnt_ft"] = NULL
                    feature["mnt_source"] = NULL
                    # layer.changeAttributeValue(feature.id(), mnt_m, NULL)
                    # layer.changeAttributeValue(feature.id(), mnt_ft, NULL)
                    # layer.changeAttributeValue(feature.id(), mnt_source, NULL)

            # layer.commitChanges(stopEditing=False)

            if feature["mnt_ft"] != NULL:
                if layer.fields().indexFromName("alt_m") != -1:
                    if feature["alt_m"] != NULL:
                        feature["hauteur_m"] = feature["alt_m"] - feature["mnt_m"]
                        # layer.changeAttributeValue(feature.id(), hauteur_m, feature["alt_m"] - feature["mnt_m"])
                if layer.fields().indexFromName("alt_ft") != -1:
                    if feature["alt_ft"] != NULL:
                        feature["hauteur_ft"] = feature["alt_ft"] - feature["mnt_ft"]
                        # layer.changeAttributeValue(feature.id(), hauteur_ft, feature["alt_ft"] - feature["mnt_ft"])

            layer.updateFeature(feature)
            # log_message(f"i : {i} / {length}")
            i += 1

        layer.commitChanges()
