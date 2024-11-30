import rasterio
from rasterio.transform import from_origin
import os

transform = rasterio.Affine(
    0.008333333300326820764,  # Pixel size in the x direction
    0.0,                      # Rotation (no rotation)
    -180.0012492646600606,    # Origin x-coordinate (west)
    0.0,                      # Rotation (no rotation)
    -0.008333333299795072507, # Pixel size in the y direction (negative for top-to-bottom)
    89.0995831776455987       # Origin y-coordinate (north)
)

# Square coordinates extend from city center
square_coords = {
    'north': (40.75782525209861, -74.006),#(lat,Long)
    'south': (40.66777439556954, -74.006),
    'east': (40.7128, -73.94682794081581),
    'west': (40.7128, -74.06517205918419)
}
# Convert square's geographic coordinates to pixel coordinates
#col = (longitude - origin_x) / pixel_size_x
#row = (latitude - origin_y) / pixel_size_y
def geographic_to_pixel(lat, lon, transform):
    # Using the inverse of the affine transform
    col, row = ~transform * (lon, lat)
    return int(col), int(row)

north_pixel = geographic_to_pixel(square_coords['north'][0], square_coords['north'][1], transform)
south_pixel = geographic_to_pixel(square_coords['south'][0], square_coords['south'][1], transform)
east_pixel = geographic_to_pixel(square_coords['east'][0], square_coords['east'][1], transform)
west_pixel = geographic_to_pixel(square_coords['west'][0], square_coords['west'][1], transform)

print("North pixel:", north_pixel)
print("South pixel:", south_pixel)
print("East pixel:", east_pixel)
print("West pixel:", west_pixel)
# Get the min and max values for the bounding box
min_col = min(north_pixel[0], south_pixel[0], east_pixel[0], west_pixel[0])
max_col = max(north_pixel[0], south_pixel[0], east_pixel[0], west_pixel[0])
min_row = min(north_pixel[1], south_pixel[1], east_pixel[1], west_pixel[1])
max_row = max(north_pixel[1], south_pixel[1], east_pixel[1], west_pixel[1])

print("Bounding box in pixel space: (min_col, min_row) to (max_col, max_row)")
print(f"({min_col}, {min_row}) to ({max_col}, {max_row})")
# Convert pixel coordinates back to geographic coordinates using the affine transform
min_lon, max_lat = transform * (min_col, min_row)  # Top-left corner
max_lon, min_lat = transform * (max_col, max_row)  # Bottom-right corner

print("Bounding box in geographic coordinates:")
print(f"West (min_lon): {min_lon}, South (min_lat): {min_lat}")
print(f"East (max_lon): {max_lon}, North (max_lat): {max_lat}")
bbox = f"{min_lon},{min_lat},{max_lon},{max_lat}"
print(bbox)
output_path = "/Users/weilynnw/Desktop/RA_new/newyork5x5"
command = f"overturemaps download --bbox={bbox} -f geojson --type=building -o {output_path}"
os.system(command)

