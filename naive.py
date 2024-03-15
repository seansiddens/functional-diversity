import geopandas as gpd
import rasterio 
from rasterio.mask import mask
import numpy as np
import time
from shapely.geometry import box
from shapely import STRtree
from tqdm import tqdm
from rasterio.plot import show
from concurrent.futures import ProcessPoolExecutor
import os
import sys
import pandas as pd

# Path to hexagon grid and GeoTIFF rasters.
SHAPEFILE_FOLDER = 'grid'
SHAPEFILE_PATH = os.path.join(SHAPEFILE_FOLDER, 'Colombia_grid_20k.shp')
RASTER_FOLDER = 'bird_maps'
rasters_to_process = [os.path.join(RASTER_FOLDER, f) for f in os.listdir(RASTER_FOLDER) if f.endswith('.tif')][:2]
print(rasters_to_process)

# Load the shapefile
print('Loading shapefile...')
start_time = time.time()
hexagons = gpd.read_file(SHAPEFILE_PATH)
num_hexagons = hexagons.shape[0]
print('Shapefile loaded in', round(time.time() - start_time, 2), 'seconds')

# Initialize dataframe for site-species matrix.
species = ["_".join(os.path.basename(raster_path).split('.')[0].split('_')[:2]) for raster_path in rasters_to_process]
site_species_matrix = pd.DataFrame(index=hexagons["GRID_ID"].tolist(), columns=species, data=0)
site_species_matrix.index.name = "GRID_ID"

# Process rasters.
procesing_start = time.time()
for raster_path in rasters_to_process:
    species_name = "_".join(os.path.basename(raster_path).split('.')[0].split('_')[:2])
    print(f'Processing raster: {os.path.basename(raster_path)}')

    # Open the raster
    start_time = time.time()
    with rasterio.open(raster_path) as src:
        # Initialize an empty list to hold indices of intersecting hexagons
        intersecting_indices = []
        raster_bounds = src.bounds
        print(f"Raster bounds: {raster_bounds}")

        # Loop through each hexagon
        for index, hexagon in tqdm(hexagons.iterrows(), total=hexagons.shape[0]):

            # Use the geometry to mask the raster, crop=True reduces the output to the bounding box of the mask
            out_image, out_transform = rasterio.mask.mask(src, [hexagon['geometry']], crop=True, nodata=0)
            
            # Check if there's any non-zero value in the masked raster
            if np.any(out_image > 0):  # Change condition based on your specific criteria
                site_species_matrix.at[hexagon["GRID_ID"], species_name] = 1
        
    total_time = time.time() - start_time
    print('Finished processing raster in', round(total_time, 2), 'seconds')


csv_output_path = 'site_species_matrix.csv'
site_species_matrix.to_csv(csv_output_path)
print(f"Site-species matrix saved to {csv_output_path}")
total_processing_time = time.time() - procesing_start
print(f"Total time: {total_processing_time} seconds")

# print(f"Average time per raster: {(total_processing_time / len(rasters_to_process))} seconds")

# print(f'Number of intersecting hexagons: {len(intersecting_hexagons)}')
# print(f"Total time: {total_time} seconds")
# print(f"Average time per hexagon: {(total_time / num_hexagons) * 1000} ms")