# Central Java Spatial-Environmental Analysis (2020–2026)

Quantitative spatial-environmental research repository analyzing two coupled environmental pressures in **Central Java (Jawa Tengah), Indonesia**:

1. **North Coast (Pantura) Shoreline Dynamics & Sediment Starvation (2020–2026)** — Multi-temporal remote sensing change detection using Sentinel-2 MSI surface reflectance in Google Earth Engine (GEE) across three climate epochs.
2. **Regional Ambient $\text{PM}_{2.5}$ Spatial Autocorrelation & Hotspot Clustering** — Spatial Autoregressive (SAR) modeling and Exploratory Spatial Data Analysis (ESDA) using Global Moran's $I$ and Local Indicators of Spatial Association (LISA) across all 35 regencies/cities (*kabupaten/kota*) in Central Java.

---

## Table of Contents

- [Project Background & Environmental Science Rationale](#project-background--environmental-science-rationale)
- [Repository Structure](#repository-structure)
- [Prerequisites & Environment Setup](#prerequisites--environment-setup)
- [Reproducing the Workflow](#reproducing-the-workflow)
- [Detailed File & Folder Reference](#detailed-file--folder-reference)
  - [Root Scripts & Data](#root-scripts--data)
  - [`gee-output/` (Google Earth Engine Exports)](#gee-output-google-earth-engine-exports)
  - [`visual/` (Publication Figures & Processed Tables)](#visual-publication-figures--processed-tables)
- [Key Quantitative Findings](#key-quantitative-findings)

---

## Project Background & Environmental Science Rationale

### 1. Coastal Abrasion vs. Accretion (Pantura, 2020–2026)
The northern coast of Central Java (*Pantai Utara* / Pantura, spanning roughly `108.80°E–111.70°E`) is a low-lying alluvial and deltaic coastline experiencing rapid geomorphic change driven by land subsidence, riverine sediment disruption, and ENSO-modulated hydro-meteorological extremes:

- **Phase 1 (2020–2023) — Triple-Dip La Niña & May 2022 Tidal Surge (*Rob*):** Elevated sea levels and intense coastal wave energy caused `1,364.11 ha` of erosion, yet high fluvial sediment discharge sustained `2,471.19 ha` of accretion, yielding a **net positive sediment budget (`+1,107.08 ha`)**.
- **Phase 2 (2023–2026) — Super El Niño & Sediment Deficit:** Prolonged drought reduced riverine sediment supply to the littoral zone (*sediment starvation*). Accretion dropped by **44.3%** (`1,375.86 ha`) while erosion surged by **40.4%** (`1,915.42 ha`), flipping the coastline past a **crossover tipping point** into a **net erosion deficit (`-539.55 ha`)**.

### 2. Ambient $\text{PM}_{2.5}$ Spatial Autocorrelation Across 35 Regencies/Cities
Air pollution in Central Java exhibits strong spatial spillover and topographic trapping. Industrial and transport corridors along the low-elevation Pantura coast (plus Surakarta and Cilacap) generate elevated $\text{PM}_{2.5}$ concentrations that diffuse into neighboring jurisdictions, whereas high-elevation inland basins/highlands (e.g., Wonosobo, Temanggung, Salatiga, Magelang) experience lower concentrations. Modeling this via a Spatial Autoregressive (SAR) process and testing with Moran's $I$ / LISA distinguishes true **High-High hotspots** from **Low-Low coldspots**.

---

## Repository Structure

```text
Research/
├── README.md
├── gee-script.js                                  # Google Earth Engine shoreline change detection script
├── preprocessing-abrasi.py                        # Coastal sediment budget & trajectory plotting script
├── simulate-air-quality.py                        # SAR PM2.5 simulation, Moran's I & LISA mapping script
├── jawa_tengah_kabkot.geojson                     # Administrative polygons for 35 Central Java kab/kota
├── gee-output/
│   ├── citra_rgb_pantura_jateng_2026.tif          # 2026 Sentinel-2 RGB composite GeoTIFF
│   ├── raster_abrasi_jateng_2020_2026.tif         # Binary coastal erosion raster (1 = erosion, 0 = other)
│   └── tabel_statistik_abrasi_jateng_2020_2026.csv# Epoch-level erosion & accretion areas (hectares)
└── visual/
    ├── sediment_budget_balance.png                # Diverging bar + net balance chart
    ├── coastal_scissors_trajectory.png            # Erosion vs. accretion crossover slopegraph
    ├── air_quality_geomap_lisa.png                # LISA cluster choropleth (High-High / Low-Low)
    ├── air_quality_geomap_pm25.png                # Continuous simulated PM2.5 choropleth map
    ├── air_quality_moran_scatter.png              # Global Moran's I scatter plot
    └── simulated_air_quality_jateng.csv           # Simulated PM2.5 & status table (35 kab/kota)
```

---

## Prerequisites & Environment Setup

### 1. Google Earth Engine (for `gee-script.js`)
- A Google Earth Engine account with access to the [GEE Code Editor](https://code.earthengine.google.com/).
- Google Drive space for exporting `.tif` and `.csv` outputs (exported to folder `GEE_Projek_Statling_Jateng`).

### 2. Python Environment (for `preprocessing-abrasi.py` & `simulate-air-quality.py`)
- **Python 3.9+** recommended.
- Install required packages:

```bash
pip install numpy pandas matplotlib geopandas libpysal esda
```

> **Note on `preprocessing-abrasi.py` path:** Line 5 currently references an absolute Windows path to `gee-output/tabel_statistik_abrasi_jateng_2020_2026.csv` (with a built-in fallback to the exact rounded Phase 1/Phase 2 values if the path is not found on another machine). Update `file_path` to a relative path (`"gee-output/tabel_statistik_abrasi_jateng_2020_2026.csv"`) if running from the repository root on a different OS or directory.

---

## Reproducing the Workflow

1. **(Optional) Re-run Remote Sensing Extraction in GEE:**
   - Open `gee-script.js` in the GEE Code Editor and click **Run**.
   - Start the three export tasks in the **Tasks** tab to regenerate the GeoTIFFs and CSV in Google Drive, then place them in `gee-output/`.
2. **Generate Coastal Sediment Figures:**
   ```bash
   python preprocessing-abrasi.py
   ```
   Outputs `visual/sediment_budget_balance.png` and `visual/coastal_scissors_trajectory.png`.
3. **Run Air Quality SAR Simulation & LISA Maps:**
   ```bash
   python simulate-air-quality.py
   ```
   Prints Global Moran's $I$ and permutation $p$-value to stdout and outputs `visual/air_quality_geomap_lisa.png` and `visual/air_quality_geomap_pm25.png`.

---

## Detailed File & Folder Reference

### Root Scripts & Data

- **`gee-script.js`**
  - **Purpose:** Multi-temporal coastal change detection along the Central Java northern shoreline (`jatengCoastROI`: `108.80°E–111.70°E`, `6.40°S–6.95°S`).
  - **Methodology:**
    - Pulls `COPERNICUS/S2_SR_HARMONIZED` dry-season composites (**June 1 – September 30**) for **2020**, **2023**, and **2026** with scene cloud cover `< 25%`.
    - Applies `QA60` bitmask cloud/cirrus removal (bits 10 and 11), reflectance scaling (`/ 10000`), and per-pixel `.median()` compositing.
    - Computes the Modified Normalized Difference Water Index: $\text{MNDWI} = \frac{B3 - B11}{B3 + B11}$, classifying water where $\text{MNDWI} > 0$.
    - Derives land-to-water transitions (**abrasion/erosion**) and water-to-land transitions (**accretion**) for Phase 1 (`2020–2023`), Phase 2 (`2023–2026`), and Cumulative Total (`2020–2026`), then sums pixel area in hectares at `20 m` resolution.
    - Exports two GeoTIFFs and one summary CSV to Google Drive (`GEE_Projek_Statling_Jateng`).

- **`preprocessing-abrasi.py`**
  - **Purpose:** Ingests `gee-output/tabel_statistik_abrasi_jateng_2020_2026.csv` and produces publication-ready charts (300 DPI) in `visual/`.
  - **Outputs:** `visual/sediment_budget_balance.png` and `visual/coastal_scissors_trajectory.png`.

- **`simulate-air-quality.py`**
  - **Purpose:** Simulates regional $\text{PM}_{2.5}$ concentrations across Central Java's 35 regencies/cities and performs spatial autocorrelation diagnostics.
  - **Methodology:**
    - Loads `jawa_tengah_kabkot.geojson` (auto-downloads from GitHub if missing), filters to `Jawa Tengah`, and drops the non-administrative `Waduk Kedungombo` polygon.
    - Assigns an `industrial_corridor` indicator (16 Pantura/industrial regencies/cities + Cilacap & Surakarta) and approximate `elevation_m` per jurisdiction.
    - Constructs a row-standardized inverse-distance spatial weight matrix $W_{\text{std}}$ from polygon centroids and generates $\text{PM}_{2.5}$ via a Spatial Autoregressive (SAR) DGP (`seed=42`, $\rho = 0.45$, $\sigma = 3.5$):
      $$y = (I - \rho W_{\text{std}})^{-1} (X\beta + \varepsilon), \quad X\beta = 20.0 + 34.0 \cdot \text{industrial\_corridor} - 0.02 \cdot \text{elevation\_m}$$
    - Computes Global Moran's $I$ and Local Moran's $I$ (LISA, $\alpha = 0.05$) using a row-standardized $k=4$ nearest-neighbor matrix (`libpysal.weights.KNN`).
  - **Outputs:** `visual/air_quality_geomap_lisa.png` and `visual/air_quality_geomap_pm25.png` (plus console output of Global Moran's $I$ and $p$-value).

- **`jawa_tengah_kabkot.geojson`**
  - **Purpose:** Administrative boundary polygon GeoJSON for Central Java's 35 regencies and cities (*kabupaten/kota*), used by `GeoPandas` for centroid extraction, spatial weights construction, and choropleth rendering.

---

### `gee-output/` (Google Earth Engine Exports)

- **`citra_rgb_pantura_jateng_2026.tif`**
  - High-resolution (`20 m`) true-color Sentinel-2 RGB composite (`B4`, `B3`, `B2`, stretched `0.0–0.28`) of the 2026 dry-season Pantura coastline for visual reference and GIS overlay.
- **`raster_abrasi_jateng_2020_2026.tif`**
  - Binary GeoTIFF (`20 m` resolution, byte-encoded) mapping cumulative 2020–2026 coastal erosion (`1` = land-to-water loss, `0` = non-erosion).
- **`tabel_statistik_abrasi_jateng_2020_2026.csv`**
  - Quantitative summary table of erosion (`Luas_Abrasi_Ha`) and accretion (`Luas_Akresi_Ha`) in hectares across `Fase 1 (2020-2023)`, `Fase 2 (2023-2026)`, and `Total (2020-2026)`.

---

### `visual/` (Publication Figures & Processed Tables)

- **`sediment_budget_balance.png`**
  - Diverging bar chart comparing coastal accretion (`+ha`, teal) vs. erosion (`-ha`, red) across Phase 1 and Phase 2, overlaid with a dashed **Net Balance** trajectory showing the flip from `+1,107 ha` to `-540 ha`.
- **`coastal_scissors_trajectory.png`**
  - Slopegraph highlighting the **Sediment Starvation Crossover Point**, where accretion drops `-44%` while erosion climbs `+40%` between Phase 1 and Phase 2.
- **`air_quality_geomap_lisa.png`**
  - Administrative choropleth map of LISA spatial clusters (`High-High (Hotspot)` in red, `Low-Low (Coldspot)` in blue, `Not Significant` in light gray), annotated with cluster names, Global Moran's $I$, and $p$-value.
- **`air_quality_geomap_pm25.png`**
  - Continuous choropleth map (`YlOrRd` palette) displaying simulated $\text{PM}_{2.5}$ ($\mu\text{g/m}^3$) across all 35 Central Java regencies/cities.
- **`air_quality_moran_scatter.png`**
  - Moran's $I$ scatter plot illustrating standardized $\text{PM}_{2.5}$ vs. its spatial lag, confirming positive spatial autocorrelation.
- **`simulated_air_quality_jateng.csv`**
  - Clean tabular dataset for all 35 Central Java regencies/cities containing columns: `region`, `lon`, `lat`, `industrial_corridor`, `elevation_m`, `pm25`, and `air_quality_status` (`Unhealthy` vs. `Moderate`).

---

## Key Quantitative Findings

| Metric / Epoch | Erosion (ha) | Accretion (ha) | Net Sediment Balance (ha) |
| :--- | :---: | :---: | :---: |
| **Phase 1 (2020–2023)** — *La Niña & Rob* | `1,364.11` | `2,471.19` | **`+1,107.08`** (Net Accretion) |
| **Phase 2 (2023–2026)** — *Super El Niño* | `1,915.42` | `1,375.86` | **`-539.55`** (Net Erosion) |
| **Cumulative (2020–2026)** | `2,034.10` | `2,601.62` | **`+567.52`** |
