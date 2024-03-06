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


# Path to your shapefile and GeoTIFF
shapefile_path = 'grid/Colombia_grid_20k.shp'
raster_path = 'bird_maps/Accipiter_bicolor_sp_range.tif'

# Load the shapefile
print('Loading shapefile...')
start_time = time.time()
hexagons = gpd.read_file(shapefile_path)
num_hexagons = hexagons.shape[0]
print('Shapefile loaded in', round(time.time() - start_time, 2), 'seconds')


# Open the raster
start_time = time.time()
with rasterio.open(raster_path) as src:
    # Initialize an empty list to hold indices of intersecting hexagons
    intersecting_indices = []
    raster_bounds = src.bounds
    print(f"Raster bounds: {raster_bounds}")

    # Loop through each hexagon
    for index, hexagon in tqdm(hexagons.iterrows(), total=hexagons.shape[0]):
        print(hexagon['geometry'])

        # Use the geometry to mask the raster, crop=True reduces the output to the bounding box of the mask
        out_image, out_transform = rasterio.mask.mask(src, [hexagon['geometry']], crop=True, nodata=0)
        
        # Check if there's any non-zero value in the masked raster
        if np.any(out_image > 0):  # Change condition based on your specific criteria
            intersecting_indices.append(index)
    
    # Filter hexagons by the indices of intersecting ones
    intersecting_hexagons = hexagons.loc[intersecting_indices]
total_time = time.time() - start_time

print(f'Number of intersecting hexagons: {len(intersecting_hexagons)}')
print(f"Total time: {total_time} seconds")
print(f"Average time per hexagon: {(total_time / num_hexagons) * 1000} ms")