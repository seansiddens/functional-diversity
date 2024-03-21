import geopandas as gpd
import rasterio 
from rasterio.mask import mask
import numpy as np
import time
from shapely.geometry import box
from shapely import STRtree
from tqdm import tqdm
from rasterio.plot import show
import concurrent.futures
import os
import sys
import pandas as pd

def process_raster(raster_path, species_name, hexagons):
    print("Processing raster: ", raster_path)
    intersection_info = {
        "species": species_name,
        "intersecting_hexagons": [] 
    }

    with rasterio.open(raster_path) as src:
        # Loop through each hexagon
        count = 0
        for _, hexagon in tqdm(hexagons.iterrows(), total=hexagons.shape[0]):
            # if count > 1_000:
            #     break
            # Use the geometry to mask the raster, crop=True reduces the output to the bounding box of the mask
            out_image, out_transform = rasterio.mask.mask(src, [hexagon['geometry']], crop=True, nodata=0)
            
            # Check if there's any non-zero value in the masked raster
            if np.any(out_image > 0):  # Change condition based on your specific criteria
                intersection_info["intersecting_hexagons"].append(hexagon["GRID_ID"])
            count += 1
    return intersection_info

def update_site_species_matrix(site_species_matrix, intersection_info):
    species = intersection_info["species"]
    # Check if the species column exists; if not, initialize it with zeros
    if species not in site_species_matrix.columns:
        site_species_matrix[species] = 0

    for hexagon_id in intersection_info["intersecting_hexagons"]:
        site_species_matrix.at[hexagon_id, species] = 1

def main():
    # Path to hexagon grid and GeoTIFF rasters.
    SHAPEFILE_FOLDER = 'grid'
    SHAPEFILE_PATH = os.path.join(SHAPEFILE_FOLDER, 'Colombia_grid_20k.shp')
    RASTER_FOLDER = 'bird_maps'
    RASTERS = [os.path.join(RASTER_FOLDER, f) for f in os.listdir(RASTER_FOLDER) if f.endswith('.tif')]
    print(f"Number of total species rasters: {len(RASTERS)}")
    SPECIES_RASTER_MAP = { "_".join(os.path.basename(raster_path).split('.')[0].split('_')[:2]): raster_path for raster_path in RASTERS }
    # Set to None if you want to generate a new matrix instead of updating an existant one.
    SITE_SPECIES_MATRIX_PATH = 'site_species_matrix.csv'
    # print(rasters_to_process)

    # Load the shapefile
    print('Loading shapefile...')
    start_time = time.time()
    hexagons = gpd.read_file(SHAPEFILE_PATH)
    print('Shapefile loaded in', round(time.time() - start_time, 2), 'seconds')

    # Initialize dataframe for site-species matrix.
    if SITE_SPECIES_MATRIX_PATH is not None:
        print('Loading site-species matrix...')
        site_species_matrix = pd.read_csv(SITE_SPECIES_MATRIX_PATH, index_col="GRID_ID")
        print(f"Species already processed: {site_species_matrix.columns.tolist()}")
        # Only process species that are not already in the matrix.
        species_to_process = [species for species in SPECIES_RASTER_MAP.keys() if species not in site_species_matrix.columns]
        print(f"Number of species to process: {len(species_to_process)}")
    else:
        print("Creating a new site-species matrix.")
        # Create a new site-species matrix
        site_species_matrix = pd.DataFrame(index=hexagons["GRID_ID"].tolist())
        site_species_matrix.index.name = "GRID_ID"
        species_to_process = [species for species in SPECIES_RASTER_MAP.keys()]

    csv_output_path = 'site_species_matrix.csv'

    if len(species_to_process) == 0:
        print("All species have already been processed.")
        return
    
    processing_start = time.time() 
    for i, species in enumerate(species_to_process):
        intersection_info = process_raster(SPECIES_RASTER_MAP[species], species, hexagons)
        update_site_species_matrix(site_species_matrix, intersection_info)

        if i % 10 == 0:
            print(f"Processed {i} species out of {len(species_to_process)}")
            site_species_matrix.to_csv(csv_output_path)

    processing_total = time.time() - processing_start
    site_species_matrix.to_csv(csv_output_path)
    print(f"Site-species matrix saved to {csv_output_path}")
    print(f"Processing time: {processing_total} seconds")
    print(f"Time per raster: {processing_total / len(species_to_process)} seconds")

if __name__ == "__main__":
    main()