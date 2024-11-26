import geopandas as gpd

# Load the data
buildings = gpd.read_file("/Users/weilynnw/Desktop/RA_new/area_of_interest/area_of_interest")

# Reproject the geometries to the desired CRS
buildings = buildings.to_crs(epsg=3857)

# Calculate the area in square meters and add it as a new column
buildings["area_sqm"] = buildings.geometry.area

# Save the desired columns to a CSV file
buildings[["geometry", "id", "area_sqm"]].to_csv("/Users/weilynnw/Desktop/RA_new/area_of_interest/buildings_area.csv", index=False)

print("Data saved successfully to buildings_area.csv")
