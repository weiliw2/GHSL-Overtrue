import rasterio
import geopandas as gpd
import rasterstats
import numpy as np
import pandas as pd

raster_path = "/Users/weilynnw/Desktop/GHSL:overtrue/cuttingGHSL/GHS_BUILT_S_E2020_GLOBE_R2023A_4326_30ss_V1_0.tif"
with rasterio.open(raster_path) as src:
    raster_array = src.read(1)
    raster_meta = src.meta
    raster_transform = src.transform
    raster_nodata = src.nodata if src.nodata is not None else -999

# Load GeoJSON file (multiple locations)
polygon_path = "/Users/weilynnw/Desktop/GHSL:overtrue/Grosshall.geojson"
buildings = gpd.read_file(polygon_path)

# Reproject all buildings to EPSG:6933 (global meter-based projection)
buildings = buildings.to_crs(epsg=6933)
print("Current CRS:", buildings.crs)

# Compute area for each polygon
buildings["area_m2"] = buildings.geometry.area

# Summarize total building area per grid cell
stats = rasterstats.zonal_stats(
    buildings, raster_path, stats="sum",
    affine=raster_transform, nodata=raster_nodata, geojson_out=True
)

# Extract values from zonal stats
grid_sums = {i: feature["properties"]["sum"] for i, feature in enumerate(stats)}

# Compute Ratio: (Summed Building Area) / (Raster Grid Value)
results = []
for idx, row in buildings.iterrows():
    # Get raster value at polygon centroid
    grid_value = rasterstats.point_query(row.geometry.centroid, raster_path, nodata=raster_nodata)
    grid_value = grid_value[0] if grid_value else np.nan  # Extract value

    # Get the total building area in that grid cell
    building_area = grid_sums.get(idx, 0)

    # Compute ratio
    ratio = building_area / grid_value if grid_value and grid_value != 0 else np.nan

    results.append({"grid_id": idx, "building_area": building_area, "grid_value": grid_value, "ratio": ratio})

# Convert to DataFrame and display
df = pd.DataFrame(results)
df.head()#import ace_tools as tools
#tools.display_dataframe_to_user(name="Building Density Ratios", dataframe=df)

# Save to CSV (Optional)
# df.to_csv("building_density_ratios.csv", index=False)
