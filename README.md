
# ☀️ Solar Panel Angle of Incidence Formula

> A clean reference for implementing and understanding the **Angle of Incidence (AOI)** formula for solar photovoltaic modeling.

---

## 🧮 Mathematical Definition

The cosine of the angle of incidence is given by:

\[
\cos(\theta_{\text{AOI}}) = \cos(\theta_z) \cos(\theta_t) + \sin(\theta_z) \sin(\theta_t) \cos(\phi_s - \phi_p)
\]

Therefore, the angle of incidence itself is:

\[
\theta_{\text{AOI}} = \cos^{-1} \left[ \cos(\theta_z) \cos(\theta_t) + \sin(\theta_z) \sin(\theta_t) \cos(\phi_s - \phi_p) \right]
\]

---

## 📘 Variable Definitions

<table>
    <tr>
        <th>Symbol</th>
        <th>Description</th>
        <th>Python Variable</th>
        <th>Units</th>
    </tr>
    <tr>
        <td>\\( \theta_{AOI} \\)</td>
        <td>Angle of Incidence</td>
        <td><code>aoi</code></td>
        <td>degrees or radians</td>
    </tr>
    <tr>
        <td>\\( \theta_z \\)</td>
        <td>Sun Zenith Angle = 90° − Solar Elevation</td>
        <td><code>zenith</code> or <code>solar_zenith</code></td>
        <td>degrees or radians</td>
    </tr>
    <tr>
        <td>\\( \theta_t \\)</td>
        <td>Panel Tilt Angle from horizontal</td>
        <td><code>tilt</code> or <code>surface_tilt</code></td>
        <td>degrees or radians</td>
    </tr>
    <tr>
        <td>\\( \phi_s \\)</td>
        <td>Sun Azimuth Angle (from North, clockwise)</td>
        <td><code>sun_azimuth</code> or <code>azimuth</code></td>
        <td>degrees</td>
    </tr>
    <tr>
        <td>\\( \phi_p \\)</td>
        <td>Panel Azimuth Angle (0°=North, 90°=East, 180°=South, 270°=West)</td>
        <td><code>panel_azimuth</code> or <code>surface_azimuth</code></td>
        <td>degrees</td>
    </tr>
</table>

---

## 🐍 Correct Python Implementation

```python
import numpy as np

def calculate_aoi(solar_zenith, solar_azimuth, surface_tilt, surface_azimuth):
    """
    Calculate Angle of Incidence (AOI) for solar panels.

    Parameters
    ----------
    solar_zenith : float
        Solar zenith angle in degrees
    solar_azimuth : float
        Solar azimuth angle in degrees (0°=North, clockwise)
    surface_tilt : float
        Panel tilt angle from horizontal in degrees
    surface_azimuth : float
        Panel azimuth angle in degrees (0°=North, clockwise)

    Returns
    -------
    aoi : float
        Angle of incidence in degrees
    """
    # Convert degrees to radians
    sz_rad = np.radians(solar_zenith)
    st_rad = np.radians(surface_tilt)
    az_diff_rad = np.radians(solar_azimuth - surface_azimuth)

    # Compute cosine of AOI
    cos_aoi = (np.cos(sz_rad) * np.cos(st_rad) +
               np.sin(sz_rad) * np.sin(st_rad) * np.cos(az_diff_rad))

    # Prevent rounding errors
    cos_aoi = np.clip(cos_aoi, -1.0, 1.0)

    # Convert to degrees
    aoi = np.degrees(np.arccos(cos_aoi))
    return aoi

# Example
solar_zenith = 30.0      # 60° solar elevation
solar_azimuth = 180.0    # Sun in the South
surface_tilt = 45.0      # Panel tilted at 45°
surface_azimuth = 180.0  # Panel facing South

aoi = calculate_aoi(solar_zenith, solar_azimuth, surface_tilt, surface_azimuth)
print(f"Angle of Incidence: {aoi:.2f}°")



# OSM-MEPS: Solar PV

This repository contains code, data and documentation for the systematic open source modeling method for energy and power system modeling focused on solar photovoltaic (PV) generation. 
It supports analysis, simulation and visualization of energy yield for validation using open-source tools such as Python and PVLIB and site measured data from https://pvoutput.org/list.jsp?df=20241201&dt=20241231&id=84471&sid=77748&t=m&v=0.

## Overview

The project includes:
- **OSM-MEPS** (Open Source Modeling Method for Energy and Power Systems) model, derived from key steps in energy and power systems modeling and its overarching frameworks that combines first-principles thinking, the scientific method and engineering design.
- High-resolution solar PV simulations using meteorological inputs such as GHI, DNI, temperature and relative humidity.
- Comparative analysis with PVLIB model and real world solar PV energy data across multiple sites (e.g., Greece, South Africa, Australia and Kenya).
- Energy yield estimation, angle of incidence modeling and tilt-azimuth optimization.

## Requirements

- Python 3.8+
- [PVLIB](https://pvlib-python.readthedocs.io/)
- NumPy, Pandas, Matplotlib, SciPy
- Jupyter Notebook (optional for interactive exploration)

## OSM-MEPS (Open Source Modeling Method for Energy and Power Systems)

[OSM-MEPS Method Overview]

<p align="center">
  <img src="OSM-MEPS_IMAGE.JPG" width="750"/>
  <br>
  <em>Figure 1: Overview of the OSM-MEPS with its overarching frameworks.</em>
</p>

## OSM-MEPS Workflow

Below is the workflow illustrating how the model integrates data, processes, and simulations from input to output.

[OSM-MEPS Workflow]

<p align="center">
  <img src="WORKFLOW-OSM-MEPS.JPG" width="800"/>
  <br>
  <em>Figure 2: Workflow of the OSM-MEPS model from solar PV modeling.</em>
</p>

## Citing OSM-MEPS method and model

Please cite our work as follows:

P. M. Mutuku, A. L. L. Jarvis, A. G. Swanson and M. F. Khan,  "A Systematic Open Source Modeling Method for Energy and Power Systems: Solar PV Application,"  *IEEE Access*, vol. 13, pp. 131869–131908, 2025,  doi: [10.1109/ACCESS.2025.3592577 (https://doi.org/10.1109/ACCESS.2025.3592577)

## Contact

If you have any questions, suggestions, or would like to collaborate, feel free to connect with me on [LinkedIn](https://www.linkedin.com/in/peter-munyao-3251b3a4/).
