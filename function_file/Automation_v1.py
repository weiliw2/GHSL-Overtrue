import rasterio
import geopandas as gpd
import rasterstats
import numpy as np
import pandas as pd

raster_path = "/Users/weilynnw/Desktop/GHSL:overtrue/cuttingGHSL/result.tif"
with rasterio.open(raster_path) as src:
    raster_array = src.read(1)
    raster_meta = src.meta
    raster_transform = src.transform
    raster_nodata = src.nodata if src.nodata is not None else -999  # Explicitly set NoData

polygon_path = "/Users/weilynnw/Desktop/GHSL:overtrue/Grosshall.geojson"
buildings0 = gpd.read_file(polygon_path)

buildings = buildings.to_crs(epsg=6933)

print("Current CRS:", buildings.crs)

# Compute area for each polygon
buildings["area"] = buildings.geometry.area

# Summarize total building area per grid cell
stats = rasterstats.zonal_stats(
    buildings, raster_path, stats="sum",
    affine=raster_transform, nodata=raster_nodata, geojson_out=True
)
# Extract values from zonal stats
grid_sums = {feature["properties"]["fid"]: feature["properties"]["sum"] for feature in stats}

# Compute Ratio: (Summed Building Area) / (Raster Grid Value)
results = []
for idx, row in buildings.iterrows():
    grid_value = raster_array[idx // raster_array.shape[1], idx % raster_array.shape[1]]  # Extract raster value
    building_area = grid_sums.get(row.fid, 0)  # Total area in that grid cell

    if grid_value and grid_value != raster_nodata:
        ratio = building_area / grid_value if grid_value != 0 else np.nan
    else:
        ratio = np.nan

    results.append({"grid_id": row.fid, "building_area": building_area, "grid_value": grid_value, "ratio": ratio})

# Convert to DataFrame and Save
df = pd.DataFrame(results)
df.head()
#df.to_csv("building_density_ratios.csv", index=False)