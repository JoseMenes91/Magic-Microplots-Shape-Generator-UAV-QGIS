# Magic Microplots Shape Generator – UAV
<img width="1024" height="1024" alt="image" src="https://github.com/user-attachments/assets/7b86fe33-8d51-4673-a068-76cc487dc15f" />


This QGIS plugin is a tool for the automatic generation of experimental plot polygons from a point layer that defines the boundaries of a field. It is ideal for the analysis of experimental designs, allowing for seamless integration with external field data (traits) and plot design maps (field maps).

The tool generates a grid of plots, georeferences it to the field boundaries, and assigns identifiers and attributes, thus facilitating spatial analysis and data visualization.

## ✨ Features

## Key Features

-   **Plot Generation:** Creates a grid of plot polygons from four corner points.
-   **Data Integration:** Allows for the assignment of field data (`.csv`) to each plot.
-   **Flexible Numbering:** Uses a field map file (`.csv`) to assign `PlotID`s, respecting the experimental design.
-   **Geometric Adjustments:** Allows for adjusting plot size and applying a buffer to the boundaries.
-   
## 🛠 Installation

1. Download or clone this repository.
2. Copy the `microplot_generator` folder into your local QGIS plugins directory: (e.g., `C:\Users\YourUser\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`).

 <img width="651" height="341" alt="image" src="https://github.com/user-attachments/assets/06502863-1624-48f6-96f2-2e421811ab03" />
<img width="988" height="750" alt="image" src="https://github.com/user-attachments/assets/c715fc19-04e3-4601-afab-f05e53ac147a" />
<img width="839" height="262" alt="image" src="https://github.com/user-attachments/assets/69b1add6-b18a-4a74-9391-36b2198fe5ab" />
<img width="949" height="225" alt="image" src="https://github.com/user-attachments/assets/2e0f7e1f-57e6-42bf-b3b9-95533d09086e" />

3.  Restart QGIS or enable the plugin from the Plugin Manager

<img width="1107" height="629" alt="image" src="https://github.com/user-attachments/assets/87ae1200-4611-4805-bb65-ea7a8a9b1c8a" />

## 📋 Usage

1. Open the plugin via `Plugins → Magic Microplots Shape Generator – UAV`.
<img width="503" height="197" alt="image" src="https://github.com/user-attachments/assets/a3c2f2a0-ad30-4413-8731-812bd0471d4a" />

2. Select the 4 corner points on your field map, in order:  
   - Top Left → Top Right → Bottom Right → Bottom Left.
   ✅ When you click each point, a red cross will appear on the map canvas
to confirm the selected location.

> 📍 **Tip:** Tip: For improved grid alignment, place the corner points before the first crop row and after the last crop row, positioning them in the inter-row space rather than directly over planted rows. This ensures that the generated grid fully covers all plots without cutting into the outer rows. traduci

<img width="776" height="325" alt="image" src="https://github.com/user-attachments/assets/3d85eb80-0113-49f1-809f-b034e3245120" />

<img width="565" height="611" alt="image" src="https://github.com/user-attachments/assets/40c857a2-c7eb-4f04-a346-b14c6d83f235" />






3. - Number of rows and columns: define according to your field design.  
     The total number of plots = number of rows × number of columns.
     For example, if your trial has 72 plots arranged in 6 rows and 12 columns, enter:
     ```
     Rows: 6
     Columns: 12
    

- Plot length and width (in meters): optional.  
  - If left empty or set to `0`, the plugin will automatically fill the area 
    between the 4 selected corner points with equally sized plots.
    <img width="1061" height="837" alt="image" src="https://github.com/user-attachments/assets/e36dc694-7827-4d32-a2bc-26cc8dc053bb" />

  - If you specify plot length and width, the plugin will generate plots 
    with those exact dimensions, positioned to fit the area.
   <img width="803" height="684" alt="image" src="https://github.com/user-attachments/assets/fffce4dd-1ea7-4e05-b5f4-7b3a36484c9b" />



  - In both cases, the centroid of each plot will be evenly distributed within the grid.
    
4. **Plot Numbering:**

- **ID Format:** choose between:
  - *Sequential*: numbers plots one after another, left to right, row by row.
<img width="1066" height="679" alt="image" src="https://github.com/user-attachments/assets/46f0b30e-3f9a-449e-979c-6e8fbbe5a7ee" />


-*Serpentine*: numbers plots in a zig-zag pattern 
    (e.g., left→right on one row, right→left on the next), 
    depending on which corner you select as the starting point.
<img width="926" height="646" alt="image" src="https://github.com/user-attachments/assets/c875aa40-2661-4eee-ad6c-09d5cae879aa" />

- **Start Numbering From:** select which corner the numbering will start from:
  - Top Left, Top Right, Bottom Left, or Bottom Right.

- **Initial ID (optional):** choose the first plot number.
  For example, if you enter `101`, numbering will start at 101 instead of 1.

5-*(Optional)### PlotID and Attribute Configuration**
- Field map CSV (for custom plot numbering):  
  This will override the automatic numbering options.  
  The CSV must contain the same number of plots as specified by the number of rows × columns.
  The numbering and layout will exactly match the order defined in the CSV,
  preserving the IDs as they appear in each row of the file.
  > 📌 The file must be a comma-separated values (CSV) file.
<img width="444" height="154" alt="image" src="https://github.com/user-attachments/assets/cf2e1711-b7f7-4170-ae96-643eb0798658" />

<img width="599" height="187" alt="image" src="https://github.com/user-attachments/assets/bb168716-8fcc-44aa-91c3-4e20a0598885" />



<img width="735" height="648" alt="image" src="https://github.com/user-attachments/assets/0a240cf2-d52d-4593-adcb-168334e20220" />

🧩 Plot data CSV (with additional information to join)

Optionally, you can upload a CSV file to add extra information to the attribute table of each generated plot.

You must select the column in your CSV that matches the PlotID assigned to each microplot in the generated layer. This column will be used to join the data.

The CSV file must be structured as follows:

Each row corresponds to one plot.

The first row must contain the column names (e.g., PLOT, EXAMPLE, BLOCK, etc.).

Additional columns can include any variable you want to associate (e.g., block, genotype, treatment, yield, etc.).

<img width="250" height="632" alt="image" src="https://github.com/user-attachments/assets/0aa75317-46b5-4a34-96ab-978f15bd9388" />

-

<img width="440" height="142" alt="image" src="https://github.com/user-attachments/assets/451230f3-b2bf-4d3c-ad77-1201ec062325" />
.

 The image shows the attribute table in QGIS, where the PLOT (PlotID) column and the example and block columns—joined from the CSV file using the plugin function—can be seen.
 .
 
<img width="510" height="671" alt="image" src="https://github.com/user-attachments/assets/af88f170-071e-4ea2-bbd3-1bab13751bea" />



💾 Output File (Optional)
In this step, you can choose a location to permanently save the generated shapefile.

If left blank, a temporary layer will be created and added to the project.
To save the file, click the ... button and choose a folder and filename.


**Citation**

José Fernando Menes, & Portillo, J. E. (2026). Magic Microplots Shape Generator – UAV (v.0.0.1). Zenodo. https://doi.org/10.5281/zenodo.18231789

<img width="455" height="88" alt="image" src="https://github.com/user-attachments/assets/02a1bb63-0b17-47bf-9470-e5d211291c42" />




