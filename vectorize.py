import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape

def vectorize_rasters(input, value, output):
    # Load the raster
    with rasterio.open(input) as src:
        image = src.read(1)
        transform = src.transform

    # Vectorize pixels not equal to 1
    mask = image != 1
    results = (
        {'properties': {'raster_val': v}, 'geometry': s}
        for i, (s, v) in enumerate(shapes(image, mask=mask, transform=transform))
    )

    # Convert to GeoDataFrame
    geoms = [shape(feature['geometry']) for feature in results]
    gdf = gpd.GeoDataFrame(geometry=geoms)

    # Dissolve geometries
    gdf_dissolved = gdf.dissolve()

    # Add 'percentile' attribute
    gdf_dissolved['value'] = value

    # Set CRS to EPSG:4326
    gdf_dissolved.set_crs(epsg=4326, inplace=True)

    # Save to a Shapefile
    gdf_dissolved.to_file(output)
