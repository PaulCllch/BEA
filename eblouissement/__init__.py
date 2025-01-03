# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Eblouissement
                                 A QGIS plugin
 Plugin QGIS de calcul de position du Soleil et d’estimation de l’éblouissement d’un pilote
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-11-06
        copyright            : (C) 2024 by ensg
        email                : paul.calloch56520@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Eblouissement class from file Eblouissement.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Eblouissement import Eblouissement   
    return Eblouissement(iface)
