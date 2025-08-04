# Magic Microplots Shape Generator – UAV
<img width="1024" height="1024" alt="image" src="https://github.com/user-attachments/assets/7b86fe33-8d51-4673-a068-76cc487dc15f" />




A QGIS plugin to generate customizable grids of microplots for agricultural trials based on user-defined parameters and corner points.  
It supports sequential and serpentine numbering, and can integrate external field data from CSV files.


## ✨ Features

- **Customizable Grid:** Specify the number of rows and columns.
- **Plot Sizing:** Define the length and width of individual plots.
- **Flexible Numbering:** Choose between sequential and serpentine numbering; set an initial ID.
- **Field Data Integration:** Load external CSV files and join them to the microplots using a common ID.
- **Intuitive Corner Selection:** Select 4 corner points directly on the map canvas.


## 🛠 Installation

1. Download or clone this repository.
2. Copy the `microplot_generator` folder into your local QGIS plugins directory: (e.g., `C:\Users\YourUser\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`).

 <img width="651" height="341" alt="image" src="https://github.com/user-attachments/assets/06502863-1624-48f6-96f2-2e421811ab03" />
<img width="988" height="750" alt="image" src="https://github.com/user-attachments/assets/c715fc19-04e3-4601-afab-f05e53ac147a" />
<img width="839" height="262" alt="image" src="https://github.com/user-attachments/assets/69b1add6-b18a-4a74-9391-36b2198fe5ab" />

3.  Restart QGIS or enable the plugin from the Plugin Manager

<img width="1107" height="629" alt="image" src="https://github.com/user-attachments/assets/87ae1200-4611-4805-bb65-ea7a8a9b1c8a" />

## 📋 Usage

1. Open the plugin via `Plugins → Magic Microplots Shape Generator – UAV`.
<img width="503" height="197" alt="image" src="https://github.com/user-attachments/assets/a3c2f2a0-ad30-4413-8731-812bd0471d4a" />

2. Select the 4 corner points on your field map, in order:  
   - Top Left → Top Right → Bottom Right → Bottom Left.
   ✅ When you click each point, a red cross will appear on the map canvas
to confirm the selected location.

> 📍 **Tip:** For better alignment, place the points in the inter-row space:  
> - before the first row (Top Left and Bottom Left), and  
> - after the last row (Top Right and Bottom Right).  
> This ensures the grid covers all plots completely without cutting into the edge rows.

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

 🧩5-*(Optional)* Load:
- Field map CSV (for custom plot numbering):  
  This will override the automatic numbering options.  
  The CSV must contain the same number of plots as specified by the number of rows × columns.
  The numbering and layout will exactly match the order defined in the CSV,
  preserving the IDs as they appear in each row of the file.
  > 📌 The file must be a comma-separated values (CSV) file.
<img width="444" height="154" alt="image" src="https://github.com/user-attachments/assets/cf2e1711-b7f7-4170-ae96-643eb0798658" />

<img width="599" height="187" alt="image" src="https://github.com/user-attachments/assets/bb168716-8fcc-44aa-91c3-4e20a0598885" />



<img width="735" height="648" alt="image" src="https://github.com/user-attachments/assets/0a240cf2-d52d-4593-adcb-168334e20220" />

- Plot data CSV (with additional information to join):
  You must select the column from your CSV that matches the plot numbering in the grid (PlotID).  
  This is the column that contains the plot numbers that the plugin will use to join the data.

You can include as many additional columns as you like in your CSV 
(e.g., block, genotype, treatment, yield, etc.).  
In the following example, the column that identifies the plots is named **"PARCELA"** (in Spanish).

<img width="327" height="616" alt="image" src="https://github.com/user-attachments/assets/92d7a437-0179-4e96-87d9-9edce9a99c00" />


  <img width="440" height="144" alt="image" src="https://github.com/user-attachments/assets/54082efb-855d-44ae-b55e-d0f1fe0fe002" />

<img width="284" height="661" alt="image" src="https://github.com/user-attachments/assets/c89c1a0a-a016-4466-9b7b-3ed64c4bc1f8" />

5. Click **Create Grid** — a new microplots layer will appear in your QGIS project.




