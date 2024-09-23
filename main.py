from percentage_change_4_weeks import *
from anomaly_formula import compute_anomaly
from reclassification import reclassify
from delete_mask import delete_mask
from download_ndvi_from_gee import download_three_ndvi_data
from vectorize import vectorize_rasters
import geopandas as gpd
from change_direction import calculate_mean
import os
from threshold import process_ndvi
from difference_based_threshold import difference_based_filter
from vectorize_all_nodata_pixels import vectorize_final_anomaly
from check_overlay import check_overlay

# delete extra files
def delete_files(file_list):
    # Get the directory of the current Python script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    for file_name in file_list:
        file_path = os.path.join(current_dir, file_name)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Successfully deleted: {file_name}")
            else:
                print(f"File not found: {file_name}")
        except Exception as e:
            print(f"Error deleting {file_name}: {str(e)}")

files_to_delete = ["anomaly.tif", "change-1.tif", "change-2.tif", "change-3.tif", "mask.tif", "total_change.tif", "week-1.tif", "week-2.tif", "week-3.tif", "week-4.tif", "final_anomaly_five_percentile.tif", "final_anomaly_ten_percentile.tif", "five_percentile_anomaly.shp", "ten_percentile_anomaly.shp", "five_percentile_anomaly.cpg", "five_percentile_anomaly.dbf", "five_percentile_anomaly.prj", "five_percentile_anomaly.shx", "ten_percentile_anomaly.cpg", "ten_percentile_anomaly.dbf", "ten_percentile_anomaly.prj", "ten_percentile_anomaly.shx", "filtered_week-3.tif", "final_anomaly_ninty_five_percentile.tif", "ninty_five_percentile_anomaly.cpg", "ninty_five_percentile_anomaly.dbf", "ninty_five_percentile_anomaly.prj", "ninty_five_percentile_anomaly.shx", "ninty_five_percentile_anomaly.shp", "vectorized_filtered_polygons.cpg", "vectorized_filtered_polygons.dbf", "vectorized_filtered_polygons.prj", "vectorized_filtered_polygons.shx", "vectorized_filtered_polygons.shp"]
shapefile_path = "small_aoi.shp"
percentiles = ['ninty_five_percentile']
start_date = '2023-11-01'
end_date = '2023-12-01'

current_directory = os.getcwd()
# This function downloads NDVI for different consecutive dates
if "week-1.tif" in os.listdir(current_directory):
    download_three_ndvi_data(shapefile_path, start_date, end_date)
else:
    pass

# This function computes percentage change week wise - returns three change TIFFs
compute_percentage_rasters()

# This function computes anomaly
compute_anomaly()

# Do Not Run Threads - Files having common names are used for multiple percentiles
for percentile in percentiles:
    
    # This function only creates a mask
    reclassify(95,100)

    # This function uses this mask to delete the unwanted pixels
    filename = delete_mask(percentile)

    # Vectorization starts here
    vectorize_rasters(filename, 5, "ninty_five_percentile_anomaly.shp")


# process_ndvi("ninty_five_percentile_anomaly.shp", "week-3.tif", "filtered_anomaly.tif")

if calculate_mean("total_change.tif") > 20:
    print("Total Change in Mean", calculate_mean("total_change.tif"))
    # If the change in NDVI between week-1 and week-3 is greater than 0.3 - only those pixels should be displayed
    difference_based_filter("week-1.tif", "week-3.tif")
    vectorize_final_anomaly()

    # Check overlap between filtered polygons and 95 percentile polygons
    check_overlay("ninty_five_percentile_anomaly.shp", "vectorized_filtered_polygons.shp")

# Deletes all files that are not 
# delete_files(files_to_delete)
