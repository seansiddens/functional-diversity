import geopandas as gpd
import pandas as pd

def save_overlapping_hexagons(matrix_csv_path, shapefile_path, output_shapefile_path, column_name):
    """
    Saves hexagons that overlap with a species (indicated by a "1" in the specified column) to a shapefile.

    Parameters:
    - matrix_csv_path: Path to the CSV file containing the site-species matrix.
    - shapefile_path: Path to the original shapefile containing all hexagons.
    - output_shapefile_path: Path where the new shapefile for the overlapping hexagons will be saved.
    - column_name: The species name (column in the CSV).
    """
    # Load the site-species matrix CSV
    matrix_df = pd.read_csv(matrix_csv_path, index_col=0)  # Ensure the first column is used as the index
    
    # Filter rows where the specified column has a value of 1
    overlapping_ids = matrix_df.index[matrix_df[column_name] == 1].tolist()
    
    # Check if any hexagons overlap with the species
    if not overlapping_ids:
        print(f"No hexagons overlap with {column_name}.")
        return

    # Load the original shapefile containing all hexagons
    hexagons = gpd.read_file(shapefile_path)
    
    # Filter the hexagons based on the overlapping IDs
    overlapping_hexagons = hexagons[hexagons.index.isin(overlapping_ids)]
    
    # Check if any hexagons were found
    if overlapping_hexagons.empty:
        print("No overlapping hexagons were found in the shapefile.")
        return
    
    # Save the overlapping hexagons to a new shapefile
    overlapping_hexagons.to_file(output_shapefile_path)
    print(f"All overlapping hexagons have been saved to {output_shapefile_path}")

def main():
    matrix_csv_path = 'site_species_matrix.csv'
    shapefile_path = 'grid/Colombia_grid_20k.shp'
    column_name = 'Galbula_tombacea'
    output_shapefile_path = f'output/{column_name}_overlapping_hexagons.shp'
    save_overlapping_hexagons(matrix_csv_path, shapefile_path, output_shapefile_path, column_name)

if __name__ == '__main__':
    main()
