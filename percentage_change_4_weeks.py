import rasterio
import numpy as np
import os

def calculate_percentage_difference(raster1, raster2, epsilon=1e-6):
    """Calculate percentage difference between two rasters, clamping output to a reasonable range."""
    # Avoid division by very small values by setting a small threshold (epsilon)
    diff = np.where(np.abs(raster1) < epsilon, 0, ((raster2 - raster1) / np.where(raster1 == 0, epsilon, raster1)) * 100)
    
    # Clamp the percentage difference to a reasonable range (-100% to +100%)
    diff = np.clip(diff, -100, 100)
    
    return diff

def read_raster(filename):
    """Read a raster file and return the data and metadata."""
    with rasterio.open(filename) as src:
        return src.read(1), src.profile

def write_raster(data, profile, filename):
    """Write data to a new raster file."""
    with rasterio.open(filename, 'w', **profile) as dst:
        dst.write(data, 1)

def compute_percentage_rasters():
    # List of input files
    input_files = ['week-1.tif', 'week-2.tif', 'week-3.tif']

    # List of intermediate output files
    change_files = ['change-1.tif', 'change-2.tif']

    # Final output file
    final_output = 'total_change.tif'

    # Read all input rasters
    rasters = [read_raster(file) for file in input_files]

    # Calculate and save percentage differences
    change_rasters = []
    for i in range(2):
        # Get data and profile for current pair of weeks
        data1, profile1 = rasters[i]
        data2, profile2 = rasters[i+1]
        
        # Calculate percentage difference
        diff = calculate_percentage_difference(data1, data2)
        
        # Update the profile for the output file
        profile1.update(dtype=rasterio.float32)
        
        # Write the difference to a new file
        write_raster(diff.astype(rasterio.float32), profile1, change_files[i])
        
        # Store the change raster for later use
        change_rasters.append(diff)

    print("Intermediate change rasters created.")

    # Sum all change rasters
    total_change = np.sum(change_rasters, axis=0)

    # Write the total change to a new file
    write_raster(total_change.astype(rasterio.float32), profile1, final_output)

    print(f"Processing complete. Final output file '{final_output}' saved in the current directory.")
