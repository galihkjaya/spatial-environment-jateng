import os
import urllib.request
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from libpysal.weights import KNN
from esda.moran import Moran, Moran_Local

output_dir = "visual"
os.makedirs(output_dir, exist_ok=True)
geojson_cache = "jawa_tengah_kabkot.geojson"

if not os.path.exists(geojson_cache):
    url = "https://raw.githubusercontent.com/azunzios/indonesia-geojson/main/indonesia_kabkota_simple.geojson"
    urllib.request.urlretrieve(url, geojson_cache)

gdf = gpd.read_file(geojson_cache)
gdf = gdf[gdf['NAME_1'] == 'Jawa Tengah'].copy()
gdf = gdf[gdf['NAME_2'] != 'Waduk Kedungombo'].copy().reset_index(drop=True)

gdf['centroid'] = gdf.geometry.centroid
gdf['lon'] = gdf['centroid'].x
gdf['lat'] = gdf['centroid'].y

pantura_industrial = [
    'Kota Semarang', 'Semarang', 'Demak', 'Kendal', 'Batang',
    'Kota Pekalongan', 'Pekalongan', 'Pemalang', 'Kota Tegal',
    'Tegal', 'Brebes', 'Kudus', 'Pati', 'Rembang', 'Jepara',
    'Cilacap', 'Surakarta'
]

elevations = {
    'Wonosobo': 780, 'Temanggung': 560, 'Salatiga': 570, 'Boyolali': 420,
    'Magelang': 360, 'Kota Magelang': 380, 'Banjarnegara': 290, 'Karanganyar': 210,
    'Klaten': 160, 'Wonogiri': 140, 'Purbalingga': 110, 'Sukoharjo': 100,
    'Surakarta': 95, 'Banyumas': 85, 'Sragen': 85, 'Blora': 60, 'Grobogan': 50,
    'Purworejo': 30, 'Kebumen': 25
}

gdf['industrial_corridor'] = gdf['NAME_2'].apply(lambda x: 1 if x in pantura_industrial else 0)
gdf['elevation_m'] = gdf['NAME_2'].apply(lambda x: elevations.get(x, 15))

np.random.seed(42)
n = len(gdf)

coords = np.column_stack((gdf['lon'].values, gdf['lat'].values))
dist_matrix = np.linalg.norm(coords[:, None, :] - coords[None, :, :], axis=-1)
np.fill_diagonal(dist_matrix, np.inf)

W = 1.0 / dist_matrix
W_std = W / W.sum(axis=1, keepdims=True)

base_pm25 = 20.0 + (gdf['industrial_corridor'] * 34.0) - (gdf['elevation_m'] * 0.02)
noise = np.random.normal(0, 3.5, size=n)
x_vec = (base_pm25 + noise).values

rho = 0.45
I = np.eye(n)
gdf['pm25'] = np.round(np.linalg.inv(I - rho * W_std).dot(x_vec), 1)

w_knn = KNN.from_dataframe(gdf, k=4)
w_knn.transform = 'R'

mi = Moran(gdf['pm25'], w_knn)
lm = Moran_Local(gdf['pm25'], w_knn, seed=42)

z_vals = (gdf['pm25'] - gdf['pm25'].mean()) / gdf['pm25'].std()
spatial_lag = np.array([sum(w_knn.weights[i][j] * z_vals.iloc[w_knn.neighbors[i][j]] for j in range(len(w_knn.neighbors[i])) ) for i in range(n)])

clusters = []
for i in range(n):
    if lm.p_sim[i] > 0.05:
        clusters.append('Not Significant')
    else:
        if z_vals.iloc[i] > 0 and spatial_lag[i] > 0:
            clusters.append('High-High (Hotspot)')
        elif z_vals.iloc[i] < 0 and spatial_lag[i] < 0:
            clusters.append('Low-Low (Coldspot)')
        elif z_vals.iloc[i] > 0 and spatial_lag[i] < 0:
            clusters.append('High-Low Outlier')
        else:
            clusters.append('Low-High Outlier')

gdf['lisa_cluster'] = clusters

print(f"Global Moran's I: {mi.I:.4f} (p-value: {mi.p_sim:.4f})")

plt.rcParams['font.family'] = 'sans-serif'

# 1. PETA CHOROPLETH LISA CLUSTERS
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

cluster_colors = {
    'High-High (Hotspot)': '#e63946',
    'Low-Low (Coldspot)': '#457b9d',
    'Not Significant': '#e5e5e5',
    'High-Low Outlier': '#f4a261',
    'Low-High Outlier': '#2a9d8f'
}

gdf['color'] = gdf['lisa_cluster'].map(cluster_colors)
gdf.plot(color=gdf['color'], edgecolor='#ffffff', linewidth=0.8, ax=ax)

for _, row in gdf[gdf['lisa_cluster'].isin(['High-High (Hotspot)', 'Low-Low (Coldspot)'])].iterrows():
    ax.annotate(row['NAME_2'], xy=(row['lon'], row['lat']),
                xytext=(0, 0), textcoords="offset points",
                ha='center', va='center', fontsize=6.8, fontweight='bold', color='#111111')

from matplotlib.patches import Patch
legend_handles = [
    Patch(facecolor=cluster_colors['High-High (Hotspot)'], edgecolor='none', label='High-High (Hotspot)'),
    Patch(facecolor=cluster_colors['Low-Low (Coldspot)'], edgecolor='none', label='Low-Low (Coldspot)'),
    Patch(facecolor=cluster_colors['Not Significant'], edgecolor='none', label='Not Significant')
]
ax.legend(handles=legend_handles, loc='lower right', frameon=False, fontsize=8.5)

ax.set_title(f"LISA Cluster Map of PM2.5 in Central Java (Moran's I = {mi.I:.3f}, p = {mi.p_sim:.3f})",
             fontsize=11, fontweight='600', pad=12, loc='left')
ax.axis('off')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "air_quality_geomap_lisa.png"), bbox_inches='tight')
plt.close()

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

gdf.plot(column='pm25', cmap='YlOrRd', edgecolor='#ffffff', linewidth=0.8,
         legend=True, legend_kwds={'label': "Simulated PM2.5 (ug/m3)", 'orientation': "horizontal", 'shrink': 0.45, 'pad': 0.05},
         ax=ax)

ax.set_title("Spatial Distribution of Simulated PM2.5 Across Central Java Regencies",
             fontsize=11, fontweight='600', pad=12, loc='left')
ax.axis('off')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "air_quality_geomap_pm25.png"), bbox_inches='tight')
plt.close()