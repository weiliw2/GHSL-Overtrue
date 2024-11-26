import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file_path = "/Users/weilynnw/Desktop/RA_new/internsectfromGis.csv"
data = pd.read_csv(file_path, usecols=['fid', 'GHSL_val', 'id', 'areaQGIS'], low_memory=False)

grouped_data = data.groupby('fid', as_index=False).agg({
    'areaQGIS': 'sum',  # Sum the area for each grid
    'GHSL_val': 'first'  # Retain the GHSL built-up area for the grid
})

grouped_data['relative_error'] = (grouped_data['GHSL_val'] - grouped_data['areaQGIS']) / grouped_data['areaQGIS']
output_path = "/Users/weilynnw/Desktop/RA_new/grouped_results.csv"
grouped_data.to_csv(output_path, index=False)

print("Analysis complete. Results saved to:", output_path)
# Remove outliers using IQR method
Q1 = grouped_data['relative_error'].quantile(0.25)
Q3 = grouped_data['relative_error'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

filtered_data = grouped_data[(grouped_data['relative_error'] >= lower_bound) &
                             (grouped_data['relative_error'] <= upper_bound)]

filtered_data['absolute_error'] = abs(filtered_data['GHSL_val'] - filtered_data['areaQGIS'])
filtered_data['squared_error'] = (filtered_data['GHSL_val'] - filtered_data['areaQGIS']) ** 2

# Calculate MAE
mae_filtered = filtered_data['absolute_error'].mean()

# Calculate RMSE
rmse_filtered = np.sqrt(filtered_data['squared_error'].mean())

print(f"Filtered Mean Absolute Error (MAE): {mae_filtered}")
print(f"Filtered Root Mean Squared Error (RMSE): {rmse_filtered}")


plt.figure(figsize=(10, 6))
plt.hist(filtered_data['relative_error'], bins=30, edgecolor='black', alpha=0.7)
plt.title('Distribution of Relative Error (Filtered)', fontsize=16)
plt.xlabel('Relative Error', fontsize=14)
plt.ylabel('Frequency', fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()
