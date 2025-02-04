from geopy.distance import geodesic
import rasterio
import os
import json

def calculate_bounding_box(city_center_point, x_km, y_km):
    latitude, longitude = city_center_point

    north = geodesic(kilometers=y_km).destination((latitude, longitude), 0).latitude
    south = geodesic(kilometers=y_km).destination((latitude, longitude), 180).latitude
    east = geodesic(kilometers=x_km).destination((latitude, longitude), 90).longitude
    west = geodesic(kilometers=x_km).destination((latitude, longitude), 270).longitude

    return (west, south, east, north)  # Format as (min_lon, min_lat, max_lon, max_lat)

transform = rasterio.Affine(
    0.008333333300326820764, 0.0, -180.0012492646600606,
    0.0, -0.008333333299795072507, 89.0995831776455987
)

# Define multiple city center locations
city_centers = [
    (36.0009, -78.9447),  # Gross Hall
    (40.7128, -74.0060),  # New York City
    (34.0522, -118.2437)  # Los Angeles
]

# Define common output path for combined GeoJSON
output_path = "/Users/weilynnw/Desktop/GHSL:overtrue/function_file/Mapbox/Combined.geojson"
all_features = []

# Loop through each city, download and merge data
for idx, city in enumerate(city_centers):
    bbox = calculate_bounding_box(city, x_km=5, y_km=5)
    bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"

    temp_output = f"/Users/weilynnw/Desktop/RA_new/temp_{idx}.geojson"
    command = f"overturemaps download --bbox={bbox_str} -f geojson --type=building -o {temp_output}"
    os.system(command)

    # Read downloaded GeoJSON and merge features
    if os.path.exists(temp_output):
        with open(temp_output, "r") as file:
            geojson_data = json.load(file)
            if "features" in geojson_data:
                all_features.extend(geojson_data["features"])

# Combine all features into one GeoJSON file
combined_geojson = {
    "type": "FeatureCollection",
    "features": all_features
}

# Save the merged GeoJSON file
with open(output_path, "w") as outfile:
    json.dump(combined_geojson, outfile, indent=4)

print(f"Combined GeoJSON saved to: {output_path}")