# OSM-MEPS: Solar PV

This repository contains code, data and documentation for the systematic open source modeling method for energy and power system modeling focused on solar photovoltaic (PV) generation. 
It supports analysis, simulation and visualization of energy yield for validation using open-source tools such as Python and PVLIB and site measured data from https://pvoutput.org/list.jsp?df=20241201&dt=20241231&id=84471&sid=77748&t=m&v=0.

## Overview

The project includes:
- **OSM-MEPS** (Open Source Modeling Method for Energy and Power Systems) model, derived from key steps in energy and power systems modeling and its overarching frameworks that combines first-principles thinking, the scientific method and engineering design.
- High-resolution solar PV simulations using meteorological inputs such as GHI, DNI, temperature and relative humidity.
- Comparative analysis with PVLIB model and real world solar PV energy data across multiple sites (e.g., Greece, South Africa, Kenya).
- Energy yield estimation, angle of incidence modeling and tilt-azimuth optimization.

## Requirements

- Python 3.8+
- [PVLIB](https://pvlib-python.readthedocs.io/)
- NumPy, Pandas, Matplotlib, SciPy
- Jupyter Notebook (optional for interactive exploration)

## OSM-MEPS (Open Source Modeling Method for Energy and Power Systems)

[OSM-MEPS Method Overview]

<p align="center">
  <br>
  <img src="OSM-MEPS_IMAGE.JPG" width="700"/>
  <em>Figure 1: Overview of the OSM-MEPS with its overarching frameworks.</em>
</p>

## OSM-MEPS Workflow

Below is the workflow illustrating how the model integrates data, processes, and simulations from input to output.

[OSM-MEPS Workflow]

<p align="center">
  <br>
  <img src="WORKFLOW-OSM-MEPS.JPG" width="900"/>
  <em>Figure 2: Workflow of the OSM-MEPS model from solar PV modeling.</em>
</p>

## Contact

If you have any questions, suggestions, or would like to collaborate, feel free to connect with me on [LinkedIn](https://www.linkedin.com/in/peter-munyao-3251b3a4/).
