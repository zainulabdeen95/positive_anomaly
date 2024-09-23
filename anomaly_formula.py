import rasterio
import numpy as np

# Open the NDVI TIFF file

def compute_anomaly():
    with rasterio.open('total_change.tif') as src:
        # Read the raster band as a numpy array
        ndvi_array = src.read(1)
        
        # Get the metadata of the source file
        profile = src.profile

    # Mask out any no-data values
    ndvi_array = np.ma.masked_invalid(ndvi_array)

    # Compute mean and standard deviation
    mean_ndvi = np.mean(ndvi_array)
    std_dev_ndvi = np.std(ndvi_array)

    # Calculate anomaly
    anomaly = (ndvi_array - mean_ndvi) / std_dev_ndvi

    # Update the profile for the new file
    profile.update(
        dtype=rasterio.float32,
        count=1,
        compress='lzw')

    # Create the new anomaly.tif file
    with rasterio.open('anomaly.tif', 'w', **profile) as dst:
        dst.write(anomaly.astype(rasterio.float32), 1)