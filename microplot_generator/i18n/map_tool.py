from qgis.gui import QgsMapToolEmitPoint
from qgis.core import QgsPointXY
from PyQt5.QtCore import Qt

class PointSelectorTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, on_point_selected_callback, add_temp_marker_callback):
        super(PointSelectorTool, self).__init__(canvas)
        self.canvas = canvas
        self.on_point_selected_callback = on_point_selected_callback
        self.add_temp_marker_callback = add_temp_marker_callback

    def canvasPressEvent(self, e):
        if e.button() == Qt.LeftButton:
            point = self.toMapCoordinates(e.pos())
            self.on_point_selected_callback(point)
            self.add_temp_marker_callback(point, 0) # This 0 will be replaced by point_number from dialog
            self.deactivate()

    def deactivate(self):
        super(PointSelectorTool, self).deactivate()

    def reset(self):
        pass
