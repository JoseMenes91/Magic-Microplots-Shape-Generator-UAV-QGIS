# -*- coding: utf-8 -*
import os

# Import necessary modules for QGIS and PyQt
import processing

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsFields,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsRectangle,
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform
)
from qgis.gui import QgsVertexMarker
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor

from .map_tool import PointSelectorTool

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'microplot_generator_dialog_base.ui'))

class MicroplotGeneratorDialog(QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        super(MicroplotGeneratorDialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)
        
        # --- DEPENDENCY CHECK (MOVED HERE) ---
        try:
            import pandas as pd
            import numpy as np
            from scipy.linalg import polar
            self.pd = pd # Store for later use
            self.np = np # Store for later use
            self.polar = polar # Store for later use
        except ImportError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Missing required Python libraries")
            msg.setInformativeText("This plugin requires 'pandas', 'numpy', and 'scipy'. Please install them in your QGIS Python environment.\n\nFor example, using the OSGeo4W Shell, you can run:\npython -m pip install pandas numpy scipy")
            msg.setWindowTitle("Dependency Error")
            msg.exec_()
            # Close the dialog if dependencies are missing
            self.close()
            return
        # --- END DEPENDENCY CHECK ---

        self.setWindowTitle(self.tr("Create Microplots Grid"))
        self.grid_params_group.setTitle(self.tr("Grid Parameters"))
        self.label.setText(self.tr("Number of Rows:"))
        self.label_2.setText(self.tr("Number of Columns:"))
        self.plot_size_group.setTitle(self.tr("Plot Size"))
        self.label_3.setText(self.tr("Plot Length (m):"))
        self.label_4.setText(self.tr("Plot Width (m):"))
        self.numbering_group.setTitle(self.tr("Plot Numbering"))
        self.label_14.setText(self.tr("ID Format:"))
        self.id_format_combobox.setItemText(0, self.tr("Sequential"))
        self.id_format_combobox.setItemText(1, self.tr("Serpentine"))
        self.label_15.setText(self.tr("Start Numbering From:"))
        self.start_numbering_combobox.setItemText(0, self.tr("Bottom Left"))
        self.start_numbering_combobox.setItemText(1, self.tr("Bottom Right"))
        self.start_numbering_combobox.setItemText(2, self.tr("Top Left"))
        self.start_numbering_combobox.setItemText(3, self.tr("Top Right"))
        self.label_16.setText(self.tr("Initial ID (optional):"))
        self.instructions_label.setText(self.tr("Click on the map to select the 4 corner points in the following order: Top Left, Top Right, Bottom Right, Bottom Left."))
        self.label_6.setText(self.tr("Point 1 (Top Left):"))
        self.select_point1_button.setText(self.tr("Select"))
        self.label_7.setText(self.tr("Point 2 (Top Right):"))
        self.select_point2_button.setText(self.tr("Select"))
        self.label_8.setText(self.tr("Point 3 (Bottom Right):"))
        self.select_point3_button.setText(self.tr("Select"))
        self.label_9.setText(self.tr("Point 4 (Bottom Left):"))
        self.select_point4_button.setText(self.tr("Select"))
        self.field_data_group.setTitle(self.tr("Field Data (Optional)"))
        self.label_fieldmap_file.setText(self.tr("Field Map File (.csv):"))
        self.label_10.setText(self.tr("Plot Data File (.csv):"))
        self.label_11.setText(self.tr("Plot ID Join Column:"))
        self.output_group.setTitle(self.tr("Output"))
        self.label_12.setText(self.tr("Output File (Optional):"))
        self.create_button.setText(self.tr("Create Grid"))

        self.selected_points = []
        self.temp_markers = []

        self.create_button.clicked.connect(self.create_grid)
        self.select_point1_button.clicked.connect(lambda: self.select_point_on_map(1))
        self.select_point2_button.clicked.connect(lambda: self.select_point_on_map(2))
        self.select_point3_button.clicked.connect(lambda: self.select_point_on_map(3))
        self.select_point4_button.clicked.connect(lambda: self.select_point_on_map(4))

        self.fieldmap_file_widget.fileChanged.connect(self.load_field_map_data)
        self.fielddata_file_widget.fileChanged.connect(self.load_field_data)
        self.fielddata_file_widget.fileChanged.connect(self.populate_plot_id_columns)

        self.field_map_df = None
        self.field_data_df = None
        self.fielddata_plotid_combobox.clear()

    def show_message(self, title, message, level=0, duration=5):
        self.iface.messageBar().pushMessage(self.tr(title), self.tr(message), level=level, duration=duration)

    def load_field_map_data(self):
        file_path = self.fieldmap_file_widget.filePath()
        if not file_path:
            self.field_map_df = None
            return
        try:
            self.field_map_df = self.pd.read_csv(file_path)
            self.show_message(self.tr("Success"), self.tr(f"Field map data loaded from {os.path.basename(file_path)}"))
        except Exception as e:
            self.show_message(self.tr("Error"), self.tr(f"Could not load field map file: {e}"), level=3)
            self.field_map_df = None

    def load_field_data(self):
        file_path = self.fielddata_file_widget.filePath()
        if not file_path:
            self.field_data_df = None
            self.fielddata_plotid_combobox.clear()
            return
        try:
            self.field_data_df = self.pd.read_csv(file_path)
            self.show_message(self.tr("Success"), self.tr(f"Field data loaded from {os.path.basename(file_path)}"))
            self.populate_plot_id_columns()
        except Exception as e:
            self.show_message(self.tr("Error"), self.tr(f"Could not load field data file: {e}"), level=3)
            self.field_data_df = None
            self.fielddata_plotid_combobox.clear()

    def populate_plot_id_columns(self):
        self.fielddata_plotid_combobox.clear()
        if self.field_data_df is not None:
            columns = self.field_data_df.columns.tolist()
            self.fielddata_plotid_combobox.addItems(columns)

    def clear_temp_markers(self):
        for marker in self.temp_markers:
            self.iface.mapCanvas().scene().removeItem(marker)
        self.temp_markers = []

    def select_point_on_map(self, point_number):
        self.map_tool = PointSelectorTool(self.iface.mapCanvas(), lambda point: self.on_point_selected(point, point_number), lambda point, idx: self.add_temp_marker(point, point_number))
        self.iface.mapCanvas().setMapTool(self.map_tool)

    def on_point_selected(self, point, point_number):
        getattr(self, f'point{point_number}_x').setText(str(self.np.round(point.x(), 2)))
        getattr(self, f'point{point_number}_y').setText(str(self.np.round(point.y(), 2)))
        self.iface.mapCanvas().unsetMapTool(self.map_tool)

    def add_temp_marker(self, point, index):
        marker = QgsVertexMarker(self.iface.mapCanvas())
        marker.setCenter(point)
        marker.setColor(QColor(255, 0, 0))
        marker.setIconSize(10)
        marker.setPenWidth(2)
        marker.setZValue(1000)
        self.temp_markers.append(marker)

    def create_grid(self):
        try:
            rows = self.rows_spinbox.value()
            cols = self.cols_spinbox.value()
            plot_length = self.length_spinbox.value()
            plot_width = self.width_spinbox.value()
            id_format = self.id_format_combobox.currentIndex()
            start_numbering_from = self.start_numbering_combobox.currentIndex()
            initial_id = self.initial_id_spinbox.value()
            fielddata_file_path = self.fielddata_file_widget.filePath()
            fielddata_plotid_col = self.fielddata_plotid_combobox.currentText()
            output_file = self.output_file_widget.filePath()
            try:
                points = [
                    QgsPointXY(float(self.point1_x.text()), float(self.point1_y.text())),
                    QgsPointXY(float(self.point2_x.text()), float(self.point2_y.text())),
                    QgsPointXY(float(self.point3_x.text()), float(self.point3_y.text())),
                    QgsPointXY(float(self.point4_x.text()), float(self.point4_y.text()))
                ]
            except ValueError:
                self.show_message(self.tr("Error"), self.tr("Please select 4 points on the map or enter valid coordinates."), level=3)
                return
            fieldmap_file_path = self.fieldmap_file_widget.filePath()
            self.generate_grid(points, rows, cols, plot_length, plot_width, output_file, self.iface.mapCanvas().mapSettings().destinationCrs(), id_format, start_numbering_from, initial_id, fielddata_file_path, fielddata_plotid_col, fieldmap_file_path)
        except Exception as e:
            self.show_message(self.tr("Error"), self.tr(f"An unexpected error occurred: {e}"), level=3)

    def generate_grid(self, corner_points, rows, cols, plot_length, plot_width, output_file, crs, id_format, start_numbering_from, initial_id, fielddata_file_path, fielddata_plotid_col, fieldmap_file_path):
        is_temporary = not bool(output_file)
        if not corner_points or len(corner_points) != 4:
            self.show_message(self.tr("Error"), self.tr("Exactly 4 corner points are required to generate the grid."), level=3)
            return

        points_layer = QgsVectorLayer(f"Point?crs={crs.authid()}", self.tr("temporary_points"), "memory")
        provider = points_layer.dataProvider()
        for p in corner_points:
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPointXY(p))
            provider.addFeature(feat)
        
        target_crs = crs
        try:
            grid_result = processing.run("qgis:creategrid", {
                'TYPE': 2,
                'EXTENT': points_layer.extent(),
                'HSPACING': points_layer.extent().width() / cols,
                'VSPACING': points_layer.extent().height() / rows,
                'CRS': target_crs,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            })
            grid = grid_result['OUTPUT']
            grid_extent = grid.extent()
        except Exception as e:
            self.show_message(self.tr("Error"), self.tr(f"Could not create initial grid: {e}"), level=3)
            return

        source_xy = self.np.array([
            [grid_extent.xMinimum(), grid_extent.yMinimum()],
            [grid_extent.xMaximum(), grid_extent.yMinimum()],
            [grid_extent.xMaximum(), grid_extent.yMaximum()],
            [grid_extent.xMinimum(), grid_extent.yMaximum()]
        ])
        
        target_xy = self.np.array([
            [corner_points[3].x(), corner_points[3].y()],
            [corner_points[2].x(), corner_points[2].y()],
            [corner_points[1].x(), corner_points[1].y()],
            [corner_points[0].x(), corner_points[0].y()]
        ])
        
        A = self.np.zeros((8, 6))
        B = self.np.zeros(8)
        for i in range(4):
            x, y = source_xy[i]
            xp, yp = target_xy[i]
            A[2 * i] = [x, y, 1, 0, 0, 0]
            B[2 * i] = xp
            A[2 * i + 1] = [0, 0, 0, x, y, 1]
            B[2 * i + 1] = yp
            
        try:
            params, _, _, _ = self.np.linalg.lstsq(A, B, rcond=None)
        except self.np.linalg.LinAlgError:
            self.show_message(self.tr("Error"), self.tr("Could not calculate transformation. Ensure points are not collinear."), level=3)
            return

        if is_temporary:
            output_layer = QgsVectorLayer(f"Polygon?crs={crs.authid()}", self.tr("Microplot Grid"), "memory")
        else:
            output_layer = QgsVectorLayer(f"Polygon?crs={crs.authid()}", os.path.basename(output_file), "ogr")
            
        provider = output_layer.dataProvider()
        fields = QgsFields()
        fields.append(QgsField("ID", QVariant.Int))
        fields.append(QgsField("PlotID", QVariant.String))
        provider.addAttributes(fields.toList())
        output_layer.updateFields()
        
        features = []
        plot_ids = []
        
        if fieldmap_file_path and os.path.exists(fieldmap_file_path):
            try:
                field_map_df = self.pd.read_csv(file_path, header=None, sep=',', engine='python')
                if field_map_df.shape != (rows, cols):
                    self.show_message(self.tr("Dimension Error"), self.tr(f"CSV has {field_map_df.shape[0]}x{field_map_df.shape[1]} but {rows}x{cols} were expected. Grid will not be generated."), level=3, duration=10)
                    return
                else:
                    plot_ids = field_map_df.values.flatten().tolist()
                    self.show_message(self.tr("Success"), self.tr(f"Using {len(plot_ids)} IDs from CSV file."), level=0, duration=10)
            except Exception as e:
                self.show_message(self.tr("Read Error"), self.tr(f"Could not process CSV: {e}. Internal numbering will be used."), level=3, duration=10)
                plot_ids = []
                
        if not plot_ids:
            self.show_message(self.tr("Info"), self.tr("Generating internal numbering."), level=0, duration=5)
            id_grid = [[0 for _ in range(cols)] for _ in range(rows)]
            current_id = initial_id
            row_iterator = list(range(rows))
            if start_numbering_from in [0, 1]:
                row_iterator.reverse()
            for r_idx, r in enumerate(row_iterator):
                col_iterator = list(range(cols))
                if start_numbering_from in [1, 3]:
                    col_iterator.reverse()
                if id_format == 1 and r_idx % 2 != 0:
                    col_iterator.reverse()
                for c in col_iterator:
                    id_grid[r][c] = current_id
                    current_id += 1
            plot_ids = [str(item) for row in id_grid for item in row]

        p1, p2, p3, p4 = corner_points[0], corner_points[1], corner_points[2], corner_points[3]
        v_col = (p2 - p1) / cols
        v_row = (p4 - p1) / rows
        
        for i in range(len(plot_ids)):
            r = i // cols
            c = i % cols
            plot_p1 = p1 + (v_row * r) + (v_col * c)
            plot_p2 = plot_p1 + v_col
            plot_p4 = plot_p1 + v_row
            plot_p3 = plot_p4 + v_col
            points = [plot_p1, plot_p2, plot_p3, plot_p4, plot_p1]
            polygon = QgsGeometry.fromPolygonXY([points])
            feat = QgsFeature()
            feat.setGeometry(polygon)
            feat.setAttributes([i + 1, str(plot_ids[i])])
            features.append(feat)
            
        provider.addFeatures(features)
        output_layer.updateExtents()
        
        if fielddata_file_path and os.path.exists(fielddata_file_path) and fielddata_plotid_col:
            try:
                field_data_df = self.pd.read_csv(fielddata_file_path)
                if fielddata_plotid_col in field_data_df.columns:
                    field_data_df[fielddata_plotid_col] = field_data_df[fielddata_plotid_col].astype(str)
                    new_fields = QgsFields()
                    for col in field_data_df.columns:
                        if col != fielddata_plotid_col:
                            if self.pd.api.types.is_numeric_dtype(field_data_df[col]):
                                new_fields.append(QgsField(col, QVariant.Double))
                            else:
                                new_fields.append(QgsField(col, QVariant.String))
                    provider.addAttributes(new_fields.toList())
                    output_layer.updateFields()
                    join_data = field_data_df.set_index(fielddata_plotid_col).to_dict('index')
                    output_layer.startEditing()
                    for feature in output_layer.getFeatures():
                        plot_id_val = feature['PlotID']
                        if plot_id_val in join_data:
                            attributes = feature.attributes()
                            row_data = join_data[plot_id_val]
                            for i, field in enumerate(output_layer.fields()):
                                field_name = field.name()
                                if field_name in row_data:
                                    attributes[i] = row_data[field_name]
                            output_layer.updateFeature(feature.id(), attributes)
                    output_layer.commitChanges()
                    self.show_message(self.tr("Success"), self.tr(f"Field data joined from {os.path.basename(fielddata_file_path)}"), level=0)
                else:
                    self.show_message(self.tr("Warning"), self.tr(f"Column '{fielddata_plotid_col}' not found in the data file. Data will not be joined."), level=2)
            except Exception as e:
                self.show_message(self.tr("Error"), self.tr(f"Could not join field data: {e}"), level=3)

        if plot_width > 0 and plot_length > 0:
            p1, p2, p4 = corner_points[0], corner_points[1], corner_points[3]
            v_right = p2 - p1
            v_down = p4 - p1
            dist_right = self.np.sqrt(v_right.x()**2 + v_right.y()**2)
            dist_down = self.np.sqrt(v_down.x()**2 + v_down.y()**2)
            if dist_right == 0 or dist_down == 0:
                self.show_message(self.tr("Error"), self.tr("Cannot define grid orientation from collinear points."), level=3)
                return
            u_right = v_right / dist_right
            u_down = v_down / dist_down
            output_layer.startEditing()
            updates = {}
            for feature in output_layer.getFeatures():
                old_geom = feature.geometry()
                centroid = old_geom.centroid().asPoint()
                half_width_vec = u_right * (plot_width / 2.0)
                half_length_vec = u_down * (plot_length / 2.0)
                new_p1 = centroid - half_width_vec - half_length_vec
                new_p2 = centroid + half_width_vec - half_length_vec
                new_p3 = centroid + half_width_vec + half_length_vec
                new_p4 = centroid - half_width_vec + half_length_vec
                new_polygon = QgsGeometry.fromPolygonXY([[new_p1, new_p2, new_p3, new_p4, new_p1]])
                updates[feature.id()] = new_polygon
            for fid, new_geom in updates.items():
                output_layer.changeGeometry(fid, new_geom)
            output_layer.commitChanges()

        QgsProject.instance().addMapLayer(output_layer)
        self.show_message(self.tr("Success"), self.tr("Grid transformed and created successfully!"), level=0)