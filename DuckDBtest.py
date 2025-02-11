import duckdb

# Connect to DuckDB (In-memory or file-based)
conn = duckdb.connect("overture_data.db")

# Install and load required extensions
conn.execute("INSTALL spatial;")
conn.execute("LOAD spatial;")
conn.execute("INSTALL azure;")  # If using Azure storage
conn.execute("LOAD azure;")

# Set Azure connection string (skip if using HTTP/S3)
conn.execute("""
SET azure_storage_connection_string = 'DefaultEndpointsProtocol=https;AccountName=overturemapswestus2;AccountKey=;EndpointSuffix=core.windows.net';
""")

# Run SQL query to filter Overture Maps data
query = """
COPY(
  SELECT
    id,
    names.primary AS primary_name,
    height,
    geometry
  FROM read_parquet('azure://release/2025-01-22.0/theme=buildings/type=building/*', filename=true, hive_partitioning=1)
  WHERE names.primary IS NOT NULL
  AND bbox.xmin BETWEEN -84.36 AND -82.42
  AND bbox.ymin BETWEEN 41.71 AND 43.33
  LIMIT 100
) TO 'detroit_buildings.geojsonseq' WITH (FORMAT GDAL, DRIVER 'GeoJSONSeq');
"""

conn.execute(query)

print("✅ Data saved as detroit_buildings.geojsonseq")
