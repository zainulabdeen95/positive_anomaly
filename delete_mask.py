import rasterio
import numpy as np

def delete_mask(filename):
    # Open the NDVI raster
    with rasterio.open('anomaly.tif') as ndvi_src:
        ndvi_data = ndvi_src.read(1)
        profile = ndvi_src.profile

    # Open the mask raster
    with rasterio.open('mask.tif') as mask_src:
        mask_data = mask_src.read(1)

    # Create the result array
    result = np.ones_like(ndvi_data)

    # Keep NDVI values where mask is "no data" (assuming "no data" is represented by 0 or np.nan)
    no_data_mask = np.isnan(mask_data) if np.isnan(mask_data).any() else (mask_data == 0)
    result[no_data_mask] = ndvi_data[no_data_mask]

    # Update the profile for the new raster
    profile.update(dtype=rasterio.float32, count=1, compress='lzw')

    # filename to save
    filename = f'final_anomaly_{filename}.tif'

    # Write the result to a new raster file
    with rasterio.open(filename, 'w', **profile) as dst:
        dst.write(result.astype(rasterio.float32), 1)

    return filename

    