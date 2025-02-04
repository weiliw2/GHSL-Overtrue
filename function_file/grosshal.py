import geopandas as gpd

# Load the GeoJSON file
geojson_path = "/Users/weilynnw/Desktop/GHSL:overtrue/Grosshall.geojson"
gdf = gpd.read_file(geojson_path)

# Ensure the data has a valid coordinate reference system (CRS)
if gdf.crs.is_geographic:
    gdf = gdf.to_crs(epsg=3857)  # Common projected CRS (Web Mercator) for area calculation

# Calculate the area for each polygon in square meters
gdf['area_sqm'] = gdf.geometry.area

# Convert the area to square kilometers (optional)
gdf['area_sqkm'] = gdf['area_sqm'] / 1e6

# Select relevant columns for CSV output
output_data = gdf[['id', 'area_sqm', 'area_sqkm']]

# Save to CSV
csv_output_path = "/Users/weilynnw/Desktop/GHSL:overtrue/Grosshall.csv"
output_data.to_csv(csv_output_path, index=False)

# Print the result to verify
print(f"Results saved to {csv_output_path}")
print(output_data.head())
