import rasterio
import numpy as np

# Open the TIFF file3
def reclassify(lower_percentile, upper_percentile):
    with rasterio.open('anomaly.tif') as src:
        ndvi = src.read(1)  # Assuming it's a single-band image
        meta = src.meta

    valid_mask = ~np.isnan(ndvi)
    valid_ndvi = ndvi[valid_mask]

    lower_threshold = np.percentile(valid_ndvi, lower_percentile)
    upper_threshold = np.percentile(valid_ndvi, upper_percentile)

    mask = np.zeros_like(ndvi, dtype=np.uint8)
    mask[valid_mask & ((ndvi <= lower_threshold) | (ndvi > upper_threshold))] = 1

    meta.update(dtype=rasterio.uint8, count=1, nodata=0)

    with rasterio.open('mask.tif', 'w', **meta) as dst:
        dst.write(mask, 1)

    print("Masked raster has been created.")
    print(f"Percentage of valid pixels with value 1: {(mask[valid_mask] == 1).mean() * 100:.2f}%")

