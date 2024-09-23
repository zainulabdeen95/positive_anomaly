import rasterio
import geopandas as gpd
from rasterio.features import shapes
import numpy as np
from shapely.ops import unary_union

def vectorize_final_anomaly():
    with rasterio.open('filtered_week-3.tif') as src:
        image = src.read(1)
        mask = (image != src.nodata) & np.isfinite(image)  # Mask valid data

        # Vectorize only valid pixels (excluding NoData and non-numeric values)
        results = (
            {'properties': {'value': v}, 'geometry': s}
            for s, v in shapes(image, mask=mask, transform=src.transform)
            if np.isfinite(v)  # Ensure pixel value is numeric
        )

        geoms = list(results)
        gdf = gpd.GeoDataFrame.from_features(geoms)

        # Dissolve all geometries into a single geometry
        dissolved = gdf.dissolve()

        # Set the CRS to EPSG:4326
        dissolved = dissolved.set_crs(src.crs).to_crs(epsg=4326)

    # Save the dissolved geometries to a shapefile
    dissolved.to_file('vectorized_filtered_polygons.shp')
