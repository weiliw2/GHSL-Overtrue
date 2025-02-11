import rasterio
import geopandas as gpd
import rasterstats
import numpy as np
import pandas as pd
from rasterio.windows import from_bounds
from shapely.geometry import box

# Load GeoJSON file (random locations)
polygon_path = "/Users/weilynnw/Desktop/GHSL:overtrue/all_cities_buildings.geojsonseq"
buildings = gpd.read_file(polygon_path)

# Load raster and keep it open
raster_path = "/Users/weilynnw/Desktop/GHSL:overtrue/cuttingGHSL/GHS_BUILT_S_E2020_GLOBE_R2023A_4326_30ss_V1_0.tif"
with rasterio.open(raster_path) as src:  
    raster_meta = src.meta
    raster_transform = src.transform
    raster_nodata = src.nodata if src.nodata is not None else -999
    raster_crs = src.crs  # Get raster CRS
    print("Raster CRS:", raster_crs)

    # Convert buildings to a projected CRS (EPSG:6933 for area calculations in meters)
    buildings = buildings.to_crs(epsg=6933)
    print("New Buildings CRS:", buildings.crs)

    # Compute area for each polygon
    buildings["area_m2"] = buildings.geometry.area

    # Convert buildings' bounding box to match the raster CRS
    bounds_geom = gpd.GeoDataFrame(geometry=[box(*buildings.total_bounds)], crs=buildings.crs)
    bounds_reprojected = bounds_geom.to_crs(raster_crs).total_bounds  # Convert bounds to raster CRS

    # Now use the corrected bounds for the raster window
    window = from_bounds(*bounds_reprojected, transform=src.transform)
    window_transform = src.window_transform(window)

    # Read only the relevant portion of the raster
    raster_array = src.read(1, window=window)

    # Summarize total building area per grid cell (using raster window)
    stats = rasterstats.zonal_stats(
        buildings, raster_path, stats="sum",
        affine=window_transform, nodata=raster_nodata, geojson_out=True
    )

    grid_sums = {i: feature["properties"]["sum"] for i, feature in enumerate(stats)}

    #(Summed Building Area) / (Raster Grid Value)
    results = []
    for idx, row in buildings.iterrows():
        grid_value = rasterstats.point_query(row.geometry.centroid, raster_path, nodata=raster_nodata)
        
        grid_value = grid_value[0] if grid_value and grid_value[0] is not None else np.nan  

        building_area = grid_sums.get(idx, 0)

        ratio = building_area / grid_value if not np.isnan(grid_value) and grid_value != 0 else np.nan

        results.append({"grid_id": idx, "building_area": building_area, "grid_value": grid_value, "ratio": ratio})

df = pd.DataFrame(results)
import ace_tools as tools
tools.display_dataframe_to_user(name="Building Density Ratios", dataframe=df)

