import geopandas as gpd
import rasterio
import numpy as np
from rasterio.mask import mask
from rasterio.transform import from_bounds
from rasterio.io import MemoryFile

def process_ndvi(shapefile, ndvi_tiff, output_tiff):
    # Read shapefile
    shapefile_polygons = gpd.read_file(shapefile)

    # Open NDVI TIFF
    with rasterio.open(ndvi_tiff) as src:
        # Read NDVI data
        ndvi_data = src.read(1)

        # TRY STANDARD DEVIATION FOR THIS!!!
        mean_ndvi = np.mean(ndvi_data[ndvi_data > 0]) #0.5

        print("NDVI Mean: ", mean_ndvi)

        # Mask NDVI using the shapefile polygons
        shapes = [geom for geom in shapefile_polygons.geometry]
        out_image, out_transform = mask(src, shapes, crop=True)
        out_image = out_image[0]

        # Find NDVI values greater than 30% of the mean within the shapefile

        threshold = (0.9 * mean_ndvi) + mean_ndvi
        mask_condition = out_image > threshold

        # Create a new array with NDVI values satisfying the condition, else set to 0
        new_ndvi = np.where(mask_condition, out_image, 0)

        # Define metadata for the new TIFF
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": new_ndvi.shape[0],
            "width": new_ndvi.shape[1],
            "transform": out_transform
        })

        # Write the new NDVI TIFF
        with rasterio.open(output_tiff, "w", **out_meta) as dest:
            dest.write(new_ndvi, 1)

# Example usage

