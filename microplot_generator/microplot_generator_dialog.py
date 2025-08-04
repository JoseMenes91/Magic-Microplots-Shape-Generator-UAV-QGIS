# -*- coding: utf-8 -*
import os
import processing
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsFields,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsVectorFileWriter,
)
from qgis.gui import QgsVertexMarker, QgsFileWidget
from PyQt5.QtGui import QColor
from .map_tool import PointSelectorTool

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'microplot_generator_dialog_base.ui'))

class MicroplotGeneratorDialog(QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        super(MicroplotGeneratorDialog, self).__init__(parent)
        self.iface = iface
        self.setupUi(self)

        try:
            import pandas as pd
            import numpy as np
            from scipy.linalg import polar
            self.pd = pd
            self.np = np
            self.polar = polar
        except ImportError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Missing required Python libraries")
            msg.setInformativeText("This plugin requires 'pandas', 'numpy', and 'scipy'. Please install them in your QGIS Python environment.\n\nFor example, using the OSGeo4W Shell, you can run:\npython -m pip install pandas numpy scipy")
            msg.setWindowTitle("Dependency Error")
            msg.exec_()
            self.close()
            return

        context = 'MicroplotGeneratorDialogBase'
        self.setWindowTitle(QCoreApplication.translate(context, "Create Microplots Grid"))
        self.grid_params_group.setTitle(QCoreApplication.translate(context, "Grid Parameters"))
        self.label.setText(QCoreApplication.translate(context, "Number of Rows:"))
        self.label_2.setText(QCoreApplication.translate(context, "Number of Columns:"))
        self.plot_size_group.setTitle(QCoreApplication.translate(context, "Plot Size"))
        self.label_3.setText(QCoreApplication.translate(context, "Plot Length (m):"))
        self.label_4.setText(QCoreApplication.translate(context, "Plot Width (m):"))
        self.numbering_group.setTitle(QCoreApplication.translate(context, "Plot Numbering"))
        self.label_14.setText(QCoreApplication.translate(context, "ID Format:"))
        self.id_format_combobox.setItemText(0, QCoreApplication.translate(context, "Sequential"))
        self.id_format_combobox.setItemText(1, QCoreApplication.translate(context, "Serpentine"))
        self.label_15.setText(QCoreApplication.translate(context, "Start Numbering From:"))
        self.start_numbering_combobox.setItemText(0, QCoreApplication.translate(context, "Bottom Left"))
        self.start_numbering_combobox.setItemText(1, QCoreApplication.translate(context, "Bottom Right"))
        self.start_numbering_combobox.setItemText(2, QCoreApplication.translate(context, "Top Left"))
        self.start_numbering_combobox.setItemText(3, QCoreApplication.translate(context, "Top Right"))
        self.label_16.setText(QCoreApplication.translate(context, "Initial ID (optional):"))
        self.instructions_label.setText(QCoreApplication.translate(context, "Click on the map to select the 4 corner points in the following order: Top Left, Top Right, Bottom Right, Bottom Left."))
        self.label_6.setText(QCoreApplication.translate(context, "Point 1 (Top Left):"))
        self.select_point1_button.setText(QCoreApplication.translate(context, "Select"))
        self.label_7.setText(QCoreApplication.translate(context, "Point 2 (Top Right):"))
        self.select_point2_button.setText(QCoreApplication.translate(context, "Select"))
        self.label_8.setText(QCoreApplication.translate(context, "Point 3 (Bottom Right):"))
        self.select_point3_button.setText(QCoreApplication.translate(context, "Select"))
        self.label_9.setText(QCoreApplication.translate(context, "Point 4 (Bottom Left):"))
        self.select_point4_button.setText(QCoreApplication.translate(context, "Select"))
        self.field_data_group.setTitle(QCoreApplication.translate(context, "Field Data (Optional)"))
        self.label_fieldmap_file.setText(QCoreApplication.translate(context, "Field Map File (.csv):"))
        self.label_10.setText(QCoreApplication.translate(context, "Plot Data File (.csv):"))
        self.label_11.setText(QCoreApplication.translate(context, "Plot ID Join Column:"))
        self.output_group.setTitle(QCoreApplication.translate(context, "Output"))
        self.label_12.setText(QCoreApplication.translate(context, "Output File (Optional):"))
        self.create_button.setText(QCoreApplication.translate(context, "Create Grid"))

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

        self.output_file_widget.setStorageMode(QgsFileWidget.SaveFile)
        self.output_file_widget.setFilter("Shapefiles (*.shp)")

        self.field_map_df = None
        self.field_data_df = None
        self.fielddata_plotid_combobox.clear()
        self.plot_ids = []
        self.plot_ids = []

    def show_message(self, title, message, level=0, duration=5):
        self.iface.messageBar().pushMessage(QCoreApplication.translate('MicroplotGeneratorDialogBase', title), QCoreApplication.translate('MicroplotGeneratorDialogBase', message), level=level, duration=duration)

    def load_field_map_data(self):
        file_path = self.fieldmap_file_widget.filePath()
        if not file_path:
            self.field_map_df = None
            return
        try:
            self.field_map_df = self.pd.read_csv(file_path)
            self.show_message("Success", f"Field map data loaded from {os.path.basename(file_path)}")
        except Exception as e:
            self.show_message("Error", f"Could not load field map file: {e}", level=3)
            self.field_map_df = None

    def load_field_data(self):
        file_path = self.fielddata_file_widget.filePath()
        if not file_path:
            self.field_data_df = None
            self.fielddata_plotid_combobox.clear()
            return
        try:
            self.field_data_df = self.pd.read_csv(file_path)
            self.show_message("Success", f"Field data loaded from {os.path.basename(file_path)}")
            self.populate_plot_id_columns()
        except Exception as e:
            self.show_message("Error", f"Could not load field data file: {e}", level=3)
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
                self.show_message("Error", "Please select 4 points on the map or enter valid coordinates.", level=3)
                return

            fieldmap_file_path = self.fieldmap_file_widget.filePath()
            self.generate_grid(points, rows, cols, plot_length, plot_width, output_file, self.iface.mapCanvas().mapSettings().destinationCrs(), id_format, start_numbering_from, initial_id, fielddata_file_path, fielddata_plotid_col, fieldmap_file_path)
        except Exception as e:
            self.show_message("Error", f"An unexpected error occurred: {e}", level=3)

    def generate_grid(self, corner_points, rows, cols, plot_length, plot_width, output_file, crs, id_format, start_numbering_from, initial_id, fielddata_file_path, fielddata_plotid_col, fieldmap_file_path):
        if not corner_points or len(corner_points) != 4:
            self.show_message("Error", "Exactly 4 corner points are required to generate the grid.", level=3)
            return

        output_layer = QgsVectorLayer(f"Polygon?crs={crs.authid()}", "Microplot Grid", "memory")

        provider = output_layer.dataProvider()
        fields = QgsFields()
        fields.append(QgsField("PlotID", QVariant.String))
        provider.addAttributes(fields.toList())
        output_layer.updateFields()

        features = []
        current_plot_ids = [] # Usar una variable local para plot_ids

        if fieldmap_file_path and os.path.exists(fieldmap_file_path):
            try:
                field_map_df = self.pd.read_csv(fieldmap_file_path, header=None, sep=',', engine='python')
                if field_map_df.shape != (rows, cols):
                    self.show_message("Dimension Error", f"CSV has {field_map_df.shape[0]}x{field_map_df.shape[1]} but {rows}x{cols} were expected. Grid will not be generated.", level=3, duration=10)
                    return
                else:
                    current_plot_ids = field_map_df.values.flatten().tolist()
                    self.show_message("Success", f"Using {len(current_plot_ids)} IDs from CSV file.", level=0, duration=10)
            except Exception as e:
                self.show_message("Read Error", f"Could not process CSV: {e}. Internal numbering will be used.", level=3, duration=10)
                current_plot_ids = []

        if not current_plot_ids:
            self.show_message("Info", "Generating internal numbering.", level=0, duration=5)
            id_grid = [[0 for _ in range(cols)] for _ in range(rows)]
            current_id = initial_id

            # Determine the order of rows to iterate for numbering
            # This is the order in which current_id will be assigned to cells in the id_grid
            numbering_row_order = list(range(rows))
            if start_numbering_from in [0, 1]: # Bottom Left, Bottom Right
                numbering_row_order.reverse() # Iterate visual rows from bottom to top

            for r_visual in numbering_row_order:
                # Determine the order of columns to iterate for numbering in this row
                numbering_col_order = list(range(cols))
                
                # Apply column reversal based on start_numbering_from (for sequential)
                if id_format == 0: # Sequential
                    if start_numbering_from in [1, 3]: # Bottom Right, Top Right
                        numbering_col_order.reverse() # Iterate visual columns from right to left
                
                # Apply serpentine logic (reverses columns for every other row based on visual row index)
                if id_format == 1: # Serpentine
                    # The serpentine effect reverses columns for every other *visual* row.
                    # If starting from Top Left (0,2) or Bottom Left (0,1) (i.e., starting left):
                    #   Row 0: Left to Right
                    #   Row 1: Right to Left
                    #   Row 2: Left to Right
                    # ...
                    # If starting from Top Right (1,3) or Bottom Right (1,3) (i.e., starting right):
                    #   Row 0: Right to Left
                    #   Row 1: Left to Right
                    #   Row 2: Right to Left
                    # ...

                    should_reverse_for_serpentine = False
                    if start_numbering_from in [0, 2]: # Starts Left (Bottom Left, Top Left)
                        if r_visual % 2 != 0: # Odd visual rows are R-L
                            should_reverse_for_serpentine = True
                    else: # Starts Right (Bottom Right, Top Right)
                        if r_visual % 2 == 0: # Even visual rows are R-L
                            should_reverse_for_serpentine = True

                    if should_reverse_for_serpentine:
                        numbering_col_order.reverse()

                for c_visual in numbering_col_order:
                    id_grid[r_visual][c_visual] = current_id
                    current_id += 1
            
            current_plot_ids = [str(item) for row in id_grid for item in row]

        # --- Lógica de generación de la cuadrícula ---
        if plot_length > 0 and plot_width > 0: # Lógica para parcelas de tamaño fijo (cálculo directo)
            p1, p2, p3, p4 = corner_points[0], corner_points[1], corner_points[2], corner_points[3]

            # Vectores para dividir la cuadrícula en celdas conceptuales
            step_x = (p2 - p1) / cols
            step_y = (p4 - p1) / rows

            # Calcular los vectores de la mitad del tamaño de la parcela, alineados con la orientación de la cuadrícula
            # Esto es para centrar la parcela en el centroide de cada celda
            half_u_horizontal_plot = (p2 - p1).normalized() * (plot_width / 2)
            half_u_vertical_plot = (p4 - p1).normalized() * (plot_length / 2)

            for i in range(rows):
                for j in range(cols):
                    # Calcular el centroide de la celda actual en la cuadrícula conceptual
                    cell_center = p1 + (step_y * (i + 0.5)) + (step_x * (j + 0.5))

                    # Calcular las cuatro esquinas de la parcela, centradas en cell_center
                    plot_p1 = cell_center - half_u_horizontal_plot - half_u_vertical_plot # Top-Left
                    plot_p2 = cell_center + half_u_horizontal_plot - half_u_vertical_plot # Top-Right
                    plot_p3 = cell_center + half_u_horizontal_plot + half_u_vertical_plot # Bottom-Right
                    plot_p4 = cell_center - half_u_horizontal_plot + half_u_vertical_plot # Bottom-Left

                    points = [plot_p1, plot_p2, plot_p3, plot_p4, plot_p1]
                    polygon = QgsGeometry.fromPolygonXY([points])

                    feat = QgsFeature()
                    feat.setGeometry(polygon)
                    plot_index = (i * cols) + j
                    if plot_index < len(current_plot_ids):
                        feat.setAttributes([str(current_plot_ids[plot_index])])
                    else:
                        self.show_message("Error", f"Plot ID not found for plot at row {i}, col {j}. Using empty ID.", level=3)
                        feat.setAttributes([""])
                    features.append(feat)

        else: # plot_length == 0 and plot_width == 0 (parcelas interpoladas simples)
            p1, p2, p3, p4 = corner_points[0], corner_points[1], corner_points[2], corner_points[3]
            v_col = (p2 - p1) / cols
            v_row = (p4 - p1) / rows

            for i in range(len(current_plot_ids)): # Usar la variable local aquí
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
                feat.setAttributes([str(current_plot_ids[i])]) # Usar la variable local aquí
                features.append(feat)

        # --- Fin de la lógica de generación de la cuadrícula ---

        provider.addFeatures(features)
        output_layer.updateExtents()

        if fielddata_file_path and os.path.exists(fielddata_file_path) and fielddata_plotid_col:
            try:
                field_data_df = self.pd.read_csv(fielddata_file_path)
                if fielddata_plotid_col in field_data_df.columns:
                    self.show_message("Info", f"Columna de unión '{fielddata_plotid_col}' encontrada en los datos de campo.", level=0)
                    field_data_df[fielddata_plotid_col] = field_data_df[fielddata_plotid_col].astype(str).str.strip().str.lower()

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
                    features_updated_count = 0
                    for feature in output_layer.getFeatures():
                        plot_id_val_layer = str(feature['PlotID']).strip().lower()
                        if plot_id_val_layer in join_data:
                            row_data = join_data[plot_id_val_layer]
                            for field_name_from_csv, value_to_set in row_data.items():
                                field_idx = output_layer.fields().indexOf(field_name_from_csv)
                                if field_idx != -1:
                                    feature.setAttribute(field_idx, value_to_set)
                                else:
                                    pass
                            output_layer.updateFeature(feature)
                            features_updated_count += 1
                        else:
                            pass
                    output_layer.commitChanges()
                    self.show_message("Éxito", f"Datos de campo unidos desde {os.path.basename(fielddata_file_path)}. {features_updated_count} entidades actualizadas.", level=0)
                    output_layer.triggerRepaint()
                    self.iface.mapCanvas().refresh()
                else:
                    self.show_message("Advertencia", f"Columna '{fielddata_plotid_col}' no encontrada en el archivo de datos. Los datos no se unirán.", level=2)
            except Exception as e:
                self.show_message("Error", f"No se pudieron unir los datos de campo: {e}", level=3)

        if output_file:
            from qgis.core import QgsVectorFileWriter
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "ESRI Shapefile"
            options.fileEncoding = "UTF-8"
            (status, error_message) = QgsVectorFileWriter.writeAsVectorFormat(output_layer, output_file, options)
            if status == QgsVectorFileWriter.NoError:
                self.show_message("Éxito", f"La cuadrícula se guardó correctamente en {output_file}")
                # Cargar la capa guardada en el proyecto
                self.iface.addVectorLayer(output_file, os.path.basename(output_file), "ogr")
            else:
                self.show_message("Error", f"No se pudo guardar la cuadrícula: {error_message}", level=3)
        else:
            QgsProject.instance().addMapLayer(output_layer)
            self.show_message("Éxito", "¡Cuadrícula creada correctamente como una capa temporal!")
