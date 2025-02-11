import duckdb
import os

# Connect to DuckDB
conn = duckdb.connect("overture_data.db")

# Install and load required extensions
conn.execute("INSTALL spatial;")
conn.execute("LOAD spatial;")
conn.execute("INSTALL azure;")
conn.execute("LOAD azure;")

# Set Azure storage connection string (skip if using HTTP/S3)
conn.execute("""
SET azure_storage_connection_string = 'DefaultEndpointsProtocol=https;AccountName=overturemapswestus2;AccountKey=;EndpointSuffix=core.windows.net';
""")

# Define multiple bounding boxes (format: [xmin, xmax, ymin, ymax])
locations = {
    "Detroit": [-84.36, -82.42, 41.71, 43.33],
    "Chicago": [-88.00, -87.50, 41.60, 42.10],
    "NewYork": [-74.10, -73.70, 40.50, 40.90]
}

# Step 1: Drop the table if it already exists to prevent conflicts
conn.execute("DROP TABLE IF EXISTS temp_buildings;")

# Step 2: Create a new temporary table
conn.execute("CREATE TABLE temp_buildings (city TEXT, id TEXT, primary_name TEXT, height DOUBLE, geometry GEOMETRY);")

# Step 3: Insert data for each city
for city, (xmin, xmax, ymin, ymax) in locations.items():
    query = f"""
      INSERT INTO temp_buildings
      SELECT
        '{city}' AS city,  -- Add a city column
        id,
        names.primary AS primary_name,
        height,
        geometry
      FROM read_parquet('azure://release/2025-01-22.0/theme=buildings/type=building/*', filename=true, hive_partitioning=1)
      WHERE names.primary IS NOT NULL
      AND bbox.xmin BETWEEN {xmin} AND {xmax}
      AND bbox.ymin BETWEEN {ymin} AND {ymax}
      LIMIT 100;
    """
    conn.execute(query)
    print(f"✅ Added {city} data to temp table")

# Step 4: Export the merged data to a single file
output_file = "/Users/weilynnw/Desktop/GHSL:overtrue/all_cities_buildings.geojsonseq"
conn.execute(f"""
COPY temp_buildings TO '{output_file}' WITH (FORMAT GDAL, DRIVER 'GeoJSONSeq');
""")

file_size = os.path.getsize(output_file) / (1024 * 1024)  # Convert bytes to MB
print(f"✅ All locations saved in {output_file} ({file_size:.2f} MB)")
