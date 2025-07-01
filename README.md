# OSM-MEPS: Solar PV

This repository contains code, data and documentation for the systematic open source modeling method for energy and power system modeling focused on solar photovoltaic (PV) generation. 
It supports analysis, simulation and visualization of energy yield for validation using open-source tools such as Python and PVLIB, and site measured data from https://pvoutput.org/list.jsp?df=20241201&dt=20241231&id=84471&sid=77748&t=m&v=0.

## Overview

The project includes:
- **OSM-MEPS** (Open Source Modeling Method for Energy and Power Systems) model, derived from key steps in modeling energy and power systems, together with an overarching framework that combines first-principles thinking, the scientific method and engineering design.
- High-resolution solar PV simulations using meteorological inputs such as GHI, DNI, temperature and relative humidity.
- Comparative analysis with PVLIB model and real world solar PV energy data across multiple sites (e.g., Greece, South Africa, Kenya).
- Energy yield estimation, angle of incidence modeling and tilt-azimuth optimization.

## Requirements

- Python 3.8+
- [PVLIB](https://pvlib-python.readthedocs.io/)
- NumPy, Pandas, Matplotlib, SciPy
- Jupyter Notebook (optional for interactive exploration)

## OSM-MEPS Modeling Framework

![OSM-MEPS Method Overview]

<p align="center">
  <img src="OSM-MEPS_IMAGE.JPG" width="600"/>
  <br>
  <em>Figure 1: Overview of the OSM-MEPS hybrid modeling framework.</em>
</p>

## OSM-MEPS Workflow

Below is the workflow illustrating how the model integrates data, processes, and simulations from input to output.

![OSM-MEPS Workflow]

<p align="center">
  <img src="WORKFLOW-OSM-MEPS.JPG" width="600"/>
  <br>
  <em>Figure 2: Workflow of the OSM-MEPS model from data input to output analysis.</em>
</p>
