import rasterio
import numpy as np

def calculate_mean(tif_path):
    with rasterio.open(tif_path) as src:
        data = src.read(1)
        mean_value = np.mean(data[data != src.nodata])
    return mean_value

