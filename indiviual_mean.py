import rasterio
import numpy as np

def calculate_mean(tif_path):
    with rasterio.open(tif_path) as src:
        data = src.read(1)
        mean_value = np.mean(data[data != src.nodata])
    return mean_value

print("Week-1", calculate_mean("week-1.tif"))
print("Week-3", calculate_mean("week-3.tif"))

print(calculate_mean("week-1.tif") - calculate_mean("week-3.tif"))