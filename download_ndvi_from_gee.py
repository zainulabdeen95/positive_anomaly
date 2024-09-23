import ee
import geemap
import os
import geopandas as gpd

def get_unique_items(input_list):
    return list(set(input_list))

# Initialize the Earth Engine API
service_account = 'agrom-ee@ee-agromai.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'agrom-ee-api-key.json')
ee.Initialize(credentials)


# Define the output folder for TIFF files
# output_folder = "NDVI"
# os.makedirs(output_folder, exist_ok=True)

def download_three_ndvi_data(shapefile_path, start_date, end_date):

    # Read the shapefile
    gdf = gpd.read_file(shapefile_path)

    # Convert the shapefile to an Earth Engine Geometry
    geometry = geemap.geopandas_to_ee(gdf)

    # Ensure geometry is of type ee.Geometry
    geometry = geometry.geometry()

    # Get Sentinel-2 Image collection
    s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")

    # Filter Sentinel-2 images
    images = s2.filterBounds(geometry) \
            .filterDate(start_date, end_date) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))

    # Extract unique dates
    def format_date(date):
        return ee.Date(date).format('YYYY-MM-dd').getInfo()

    dates = images.aggregate_array('system:time_start').getInfo()
    formatted_dates = [format_date(date) for date in dates]

    # Ensure dates are unique and sorted in ascending order
    unique_dates_list = sorted(get_unique_items(formatted_dates))

    # Mosaicking same date tiles
    def create_mosaic(date):
        startDate = ee.Date(date)
        endDate = startDate.advance(1, 'day')
        mosaic = images.filterDate(startDate, endDate).mosaic()
        return mosaic.set('date', date, 'system:time_start', startDate.millis())

    mosaic_collection = ee.ImageCollection([create_mosaic(date) for date in unique_dates_list])


    # Calculate NDVI and NDWI, add bands
    def add_indices(img):
        ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI')
        ndwi = img.normalizedDifference(['B3', 'B8']).rename('NDWI')
        return img.addBands([ndvi, ndwi]).copyProperties(img, ['system:time_start'])

    mosaic_collection = mosaic_collection.map(add_indices)

    # Ensure to get the first 4 unique dates only if they exist
    limit = 3
    limited_list = mosaic_collection.toList(limit)


    # Download NDVI images as TIFF files
    for i in range(limit):
        image = ee.Image(limited_list.get(i))
        date = image.get('date').getInfo()
        print(date)
        
        # Select NDVI band and clip to geometry
        ndvi_image = image.select('NDVI').clip(geometry)
        
        # Create a filename for the TIFF
        filename = f"week-{i+1}.tif"
        # output_path = os.path.join(output_folder, filename)
        
        # Download the image
        geemap.ee_export_image(
            ndvi_image,
            filename=filename,
            scale=10,
            region=geometry,
            file_per_band=False
        )
        
        print(f"Downloaded: {filename}")

print("All downloads completed.")
