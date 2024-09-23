import rasterio
import numpy as np

def difference_based_filter(week1_path, week3_path):
    with rasterio.open(week1_path) as src1, rasterio.open(week3_path) as src3:
        week1 = src1.read(1)
        week3 = src3.read(1)
        meta = src1.meta.copy()

    # Calculate difference and mask
    diff = week3 - week1
    mask = (diff > 0.2)

    # Apply mask to week3 for valid pixels
    week3_filtered = np.where(mask, week3, np.nan)

    # Save the result
    meta.update(dtype=rasterio.float32)

    with rasterio.open('filtered_week-3.tif', 'w', **meta) as dst:
        dst.write(week3_filtered.astype(rasterio.float32), 1)
