# Magic Microplots Shape Generator – UAV

## English

This QGIS plugin allows you to generate a grid of microplots for agricultural trials based on user-defined parameters and corner points. It supports sequential and serpentine numbering, and can integrate external field data.

### Features:

*   **Customizable Grid:** Define the number of rows and columns.
*   **Plot Sizing:** Set the length and width of individual plots.
*   **Flexible Numbering:** Choose between sequential and serpentine numbering, and set an initial ID for numbering.
*   **Field Data Integration:** Load external CSV files with plot data and join them to the generated microplots using a common ID column.
*   **Intuitive Point Selection:** Select corner points directly on the map.

### Installation:

1.  Download the plugin files.
2.  Place the `microplot_generator` folder into your QGIS plugins directory (e.g., `C:\Users\YourUser\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`).
3.  Restart QGIS or enable the plugin from the Plugin Manager.

### Usage:

1.  Open the plugin from the `Plugins -> Magic Microplots Shape Generator – UAV` menu.
2.  Enter the desired grid parameters (rows, columns, plot length, plot width).
3.  Select the 4 corner points on the map in the specified order (Top Left, Top Right, Bottom Right, Bottom Left).
4.  (Optional) Load a field map CSV and/or a plot data CSV. If loading plot data, select the column to use for joining.
5.  Click "Create Grid" to generate the microplots layer.

## Español

Este plugin de QGIS permite generar una grilla de microparcelas para ensayos agrícolas basándose en parámetros definidos por el usuario y puntos de esquina. Soporta numeración secuencial y serpentina, y puede integrar datos de campo externos.

### Características:

*   **Grilla Personalizable:** Define el número de filas y columnas.
*   **Dimensionamiento de Parcela:** Establece el largo y ancho de las parcelas individuales.
*   **Numeración Flexible:** Elige entre numeración secuencial y serpentina, y establece un ID inicial para la numeración.
*   **Integración de Datos de Campo:** Carga archivos CSV externos con datos de parcela y únelos a las microparcelas generadas usando una columna de ID común.
*   **Selección de Puntos Intuitiva:** Selecciona los puntos de esquina directamente en el mapa.

### Instalación:

1.  Descarga los archivos del plugin.
2.  Coloca la carpeta `microplot_generator` en tu directorio de plugins de QGIS (ej: `C:\Users\TuUsuario\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`).
3.  Reinicia QGIS o habilita el plugin desde el Administrador de Complementos.

### Uso:

1.  Abre el plugin desde el menú `Complementos -> Magic Microplots Shape Generator – UAV`.
2.  Introduce los parámetros de la grilla deseados (filas, columnas, largo de parcela, ancho de parcela).
3.  Selecciona los 4 puntos de esquina en el mapa en el orden especificado (Superior Izquierdo, Superior Derecho, Inferior Derecho, Inferior Izquierdo).
4.  (Opcional) Carga un CSV de mapa de campo y/o un CSV de datos de parcela. Si cargas datos de parcela, selecciona la columna a usar para la unión.
5.  Haz clic en "Crear Grilla" para generar la capa de microparcelas.
