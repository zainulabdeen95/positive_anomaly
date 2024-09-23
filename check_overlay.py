import geopandas as gpd

def check_overlay(shapefile1, shapefile2):
    # Load the two shapefiles
    gdf1 = gpd.read_file(shapefile1)
    gdf2 = gpd.read_file(shapefile2)

    # Find the geometries that overlap between the two shapefiles
    overlap = gpd.overlay(gdf1, gdf2, how='intersection')

    # Save the overlapping geometries to a new shapefile
    overlap.to_file('positive_anomaly.shp')
