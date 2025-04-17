# Rapid Processing of Hydrographic Data

This repository contains Jupyter notebooks and Python libraries designed for rapid processing, visualization, and analysis of hydrographic and bathymetric data. The tools streamline the creation of accurate, detailed marine charts from raw hydrographic survey data.

---

## Project Overview

The main goals of this project are:

- **Rapid** transformation of raw hydrographic data into validated bathymetric surfaces.
- **Automated** extraction of depth contours, soundings, and chart features.

---

## Repository Structure

```plaintext
.
├── notebooks/
│   ├── 1. UserParameters_ChartLimit.ipynb
│   ├── 2. LandAreas.ipynb
│   ├── 3. Bathymetry.ipynb
│   ├── 4. Contours_DepthAreas.ipynb
│   └── 5. Soundings.ipynb
├── input/
│   └── [input hydrographic data files]
├── output/
│   ├── Bathymetric_Features/
│   ├── Chart_Features/
│   └── Land_Features/
├── lib/
│   ├── cartographic_model.py
│   ├── domain.py
│   ├── node.py
│   ├── point.py
│   ├── pointset.py
│   ├── reader.py
│   ├── tin.py
│   ├── tree.py
│   ├── triangles.py
│   ├── utilities.py
│   └── vertex.py
├── requirements.txt
└── README.md
