from geopy.distance import geodesic
import rasterio
import os

# Function to calculate a bounding box around a city center point
def calculate_bounding_box(city_center_point, x_km, y_km):
    latitude, longitude = city_center_point

    north = geodesic(kilometers=y_km).destination((latitude, longitude), 0).latitude
    south = geodesic(kilometers=y_km).destination((latitude, longitude), 180).latitude
    east = geodesic(kilometers=x_km).destination((latitude, longitude), 90).longitude
    west = geodesic(kilometers=x_km).destination((latitude, longitude), 270).longitude

    return {
        "north": (north, longitude),
        "south": (south, longitude),
        "east": (latitude, east),
        "west": (latitude, west)
    }

# Convert geographic coordinates to pixel coordinates
def geographic_to_pixel(lat, lon, transform):
    # Using the inverse of the affine transform
    col, row = ~transform * (lon, lat)
    return int(col), int(row)

# Define the city center and distance for the bounding box
# Change the parameter()
city_center_point = (36.000904822474304, -78.94468675402734)  #gross hall coordinates
x_km = 5
y_km = 5
bounding_box = calculate_bounding_box(city_center_point, x_km, y_km)
print("Bounding Box Coordinates:", bounding_box)

# Define affine transform
transform = rasterio.Affine(
    0.008333333300326820764,  # Pixel size in the x direction
    0.0,                      # Rotation (no rotation)
    -180.0012492646600606,    # Origin x-coordinate (west)
    0.0,                      # Rotation (no rotation)
    -0.008333333299795072507, # Pixel size in the y direction (negative for top-to-bottom)
    89.0995831776455987       # Origin y-coordinate (north)
)

square_coords = bounding_box

# Convert bounding box geographic coordinates to pixel coordinates
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

# Dowload the Overture data
bbox = f"{min_lon},{min_lat},{max_lon},{max_lat}"
print("Formatted BBox:", bbox)

# Define the output path
output_path = "/Users/weilynnw/Desktop/GHSL:overtrue/singleOverture/Grosshall.geojson"
# local path "/Users/weilynnw/Desktop/GHSL:overtrue/Overtruetestarea.geojson"
command = f"overturemaps download --bbox={bbox} -f geojson --type=building -o {output_path}"
os.system(command)
