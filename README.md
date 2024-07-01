# Flow Cytometry Gating Tool

## Overview
flowGate is a Python-based tool for applying hierarchical gating to flow cytometry data. It allows users to define gating hierarchies and polygon vertices for gating, and then applies these gates to the data. The tool also supports visualizing the gates with and without density contours.

## Features
- Currently does not perform any relevant preprocessing or normalization.
- Load and process FCS files
- Define hierarchical gating structures in a JSON file
- Apply manual polygon gates to the data
- Annotate data with gate labels
- Save annotated data to CSV with binary labels of cells presence in each gate.
- Visualize gates with and without density contours

## Installation
To install the required dependencies, use the following command:
```bash
pip install pandas numpy matplotlib seaborn fcsparser
```

## Usage
 1. Define the gating hierarchy
    - Create a JSON file representing the gating hierarchy. This JSON file should resemble a tree. Each gate can have children gates, forming a hierarchical structure where gated cells are excluded from adjacent downstream gates.
    - See `gating_hierarchy.json` for an example. 
     
      - In this example cells included in `34P_38P` are excluded from all gates downstream of `34P_38N`.
 2. Run the tool from the command line:
    - Call the script with the path to the FCS file, the gating hierarchy JSON file, and the path to save the annotated CSV file. Optionally, you can also plot the gates with or without density contours.
    ```bash
    python FlowCytGating.py path_to_your_fcs_file.fcs gating_hierarchy.json annotated_cells.csv --plot --with_contours
     ``` 
 3. This process can be repeated to quickly change the vertices of each gate. 
