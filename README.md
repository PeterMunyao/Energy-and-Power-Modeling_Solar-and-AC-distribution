
<!DOCTYPE html>
<html>
<head>
    <title>Solar Panel Angle of Incidence Formula</title>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
    <h1>Angle of Incidence Formula for Solar Panels</h1>
    
    <div class="formula">
        <h2>Mathematical Definition</h2>
        <p>The cosine of the angle of incidence is given by:</p>
        \[
        \cos(\theta_{\text{AOI}}) = \cos(\theta_z) \cos(\theta_t) + \sin(\theta_z) \sin(\theta_t) \cos(\phi_s - \phi_p)
        \]
        
        <p>Therefore, the angle of incidence itself is:</p>
        \[
        \theta_{\text{AOI}} = \cos^{-1} \left[ \cos(\theta_z) \cos(\theta_t) + \sin(\theta_z) \sin(\theta_t) \cos(\phi_s - \phi_p) \right]
        \]
    </div>
    
    <div class="variables">
        <h2>Variable Definitions</h2>
        <table border="1">
            <tr>
                <th>Symbol</th>
                <th>Description</th>
                <th>Python Variable</th>
                <th>Units</th>
            </tr>
            <tr>
                <td>\(\theta_{\text{AOI}}\)</td>
                <td>Angle of Incidence</td>
                <td><code>aoi</code></td>
                <td>degrees or radians</td>
            </tr>
            <tr>
                <td>\(\theta_z\)</td>
                <td>Sun Zenith Angle = 90° - Solar Elevation</td>
                <td><code>zenith</code> or <code>solar_zenith</code></td>
                <td>degrees or radians</td>
            </tr>
            <tr>
                <td>\(\theta_t\)</td>
                <td>Panel Tilt Angle from horizontal</td>
                <td><code>tilt</code> or <code>surface_tilt</code></td>
                <td>degrees or radians</td>
            </tr>
            <tr>
                <td>\(\phi_s\)</td>
                <td>Sun Azimuth Angle (from North, clockwise)</td>
                <td><code>sun_azimuth</code> or <code>azimuth</code></td>
                <td>degrees</td>
            </tr>
            <tr>
                <td>\(\phi_p\)</td>
                <td>Panel Azimuth Angle (0°=North, 90°=East, 180°=South, 270°=West)</td>
                <td><code>panel_azimuth</code> or <code>surface_azimuth</code></td>
                <td>degrees</td>
            </tr>
        </table>
    </div>
    
    <div class="python-code">
        <h2>Correct Python Implementation</h2>
        <pre><code>
import numpy as np

def calculate_aoi(solar_zenith, solar_azimuth, surface_tilt, surface_azimuth):
    """
    Calculate Angle of Incidence for solar panels
    
    Parameters:
    -----------
    solar_zenith : float
        Solar zenith angle in degrees
    solar_azimuth : float  
        Solar azimuth angle in degrees (0°=North, clockwise)
    surface_tilt : float
        Panel tilt angle from horizontal in degrees
    surface_azimuth : float
        Panel azimuth angle in degrees (0°=North, clockwise)
    
    Returns:
    --------
    aoi : float
        Angle of incidence in degrees
    """
    
    # Convert degrees to radians for trigonometric functions
    sz_rad = np.radians(solar_zenith)
    st_rad = np.radians(surface_tilt)
    az_diff_rad = np.radians(solar_azimuth - surface_azimuth)
    
    # Calculate cosine of angle of incidence
    cos_aoi = (np.cos(sz_rad) * np.cos(st_rad) + 
               np.sin(sz_rad) * np.sin(st_rad) * np.cos(az_diff_rad))
    
    # Clamp to avoid numerical errors
    cos_aoi = np.clip(cos_aoi, -1.0, 1.0)
    
    # Calculate AOI in degrees
    aoi = np.degrees(np.arccos(cos_aoi))
    
    return aoi

# Example usage:
solar_zenith = 30.0    # 60° solar elevation
solar_azimuth = 180.0  # Sun in the South
surface_tilt = 45.0    # 45° panel tilt  
surface_azimuth = 180.0 # Panel facing South

aoi = calculate_aoi(solar_zenith, solar_azimuth, surface_tilt, surface_azimuth)
print(f"Angle of Incidence: {aoi:.2f}°")
        </code></pre>
    </div>
    
    <div class="journal-error">
        <h2>⚠️ Important Note: Journal Paper Error vs Correct Code</h2>
        <p><strong>Common Error in Journal Papers:</strong> Some papers incorrectly use:</p>
        \[
        \theta_{\text{AOI}} = \cos^{-1} \left[ \cos(\theta_z) \cos(\theta_t) + \sin(\theta_z) \sin(\theta_t) + \cos(\phi_s - \phi_p) \right]
        \]
        <p><strong>This is WRONG</strong> - the plus sign before the last cosine term should be multiplication.</p>
        
        <p><strong>Correct Implementation:</strong> The Python code above uses the proper formula with multiplication:</p>
        <p><code>cos_aoi = np.cos(sz_rad)*np.cos(st_rad) + np.sin(sz_rad)*np.sin(st_rad)*np.cos(az_diff_rad)</code></p>
        
        <p><em>Always verify the formula implementation in code, as journal papers sometimes contain typographical errors.</em></p>
    </div>
    
    <div class="derivation">
        <h2>Formula Derivation</h2>
        <p>This formula comes from spherical trigonometry and represents the dot product between:</p>
        <ul>
            <li>Sun direction vector: \((\sin\theta_z \cos\phi_s, \sin\theta_z \sin\phi_s, \cos\theta_z)\)</li>
            <li>Panel normal vector: \((\sin\theta_t \cos\phi_p, \sin\theta_t \sin\phi_p, \cos\theta_t)\)</li>
        </ul>
        <p>The dot product gives: \(\cos\theta_{\text{AOI}} = \cos\theta_z \cos\theta_t + \sin\theta_z \sin\theta_t \cos(\phi_s - \phi_p)\)</p>
    </div>
</body>
</html>



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
