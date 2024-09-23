import geopandas as gpd
import rasterio
import numpy as np
from rasterio.mask import mask

def process_ndvi(shapefile, ndvi_tiff, output_tiff):
    shapefile_polygons = gpd.read_file(shapefile)

    with rasterio.open(ndvi_tiff) as src:
        ndvi_data = src.read(1)

        mean_ndvi = np.mean(ndvi_data[ndvi_data > 0])
        std_ndvi = np.std(ndvi_data[ndvi_data > 0])

        print("Mean NDVI: ", mean_ndvi)

        shapes = [geom for geom in shapefile_polygons.geometry]
        out_image, out_transform = mask(src, shapes, crop=True)
        out_image = out_image[0]

        threshold = mean_ndvi + 2 * std_ndvi
        mask_condition = out_image > threshold

        new_ndvi = np.where(mask_condition, out_image, 0)

        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": new_ndvi.shape[0],
            "width": new_ndvi.shape[1],
            "transform": out_transform
        })

        with rasterio.open(output_tiff, "w", **out_meta) as dest:
            dest.write(new_ndvi, 1)
