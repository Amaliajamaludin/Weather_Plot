import pandas as pd  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
from calendar import month_abbr
import numpy as np  # type: ignore

# Load and preview data
df = pd.read_csv('fb441e62df2d58994928907a91895ec62c2c42e6cd075c2700843b89.csv')
print(df.head())

# Transform the Data_Value column
df['Data_Value'] = df['Data_Value'] * 0.1

# Convert Date column to datetime format if not already done
df['Date'] = pd.to_datetime(df['Date'])

# Extract and sort rows with minimum and maximum temperatures
df_tmin = df[df['Element'] == 'TMIN'].sort_values(by='Date')
df_tmax = df[df['Element'] == 'TMAX'].sort_values(by='Date')

# Keep records from 2004 to 2015 and drop February 29
df_tmin_filtered = df_tmin[(df_tmin['Date'].dt.year >= 2004) &
                           (df_tmin['Date'].dt.year <= 2015) &
                           ~((df_tmin['Date'].dt.month == 2) & (df_tmin['Date'].dt.day == 29))]

df_tmax_filtered = df_tmax[(df_tmax['Date'].dt.year >= 2004) &
                           (df_tmax['Date'].dt.year <= 2015) &
                           ~((df_tmax['Date'].dt.month == 2) & (df_tmax['Date'].dt.day == 29))]

# Compute the highest and lowest Data_Value for 2005 to 2015
df_tmin = (df_tmin_filtered[(df_tmin_filtered['Date'].dt.year >= 2005) &
                            (df_tmin_filtered['Date'].dt.year <= 2015)]
           .groupby(['Date'], as_index=False)['Data_Value'].min()[['Date', 'Data_Value']])

df_tmax = (df_tmax_filtered[(df_tmax_filtered['Date'].dt.year >= 2005) &
                            (df_tmax_filtered['Date'].dt.year <= 2015)]
           .groupby(['Date'], as_index=False)['Data_Value'].max()[['Date', 'Data_Value']])

# Separate into 2005-2014 and 2015
df_tmin_2005_2014 = df_tmin[df_tmin['Date'].dt.year < 2015]
df_tmin_2015 = df_tmin[df_tmin['Date'].dt.year == 2015]

df_tmax_2005_2014 = df_tmax[df_tmax['Date'].dt.year < 2015]
df_tmax_2015 = df_tmax[df_tmax['Date'].dt.year == 2015]

# Change Date to Month Day format
df_tmin_2005_2014['Date'] = df_tmin_2005_2014['Date'].dt.strftime('%m-%d')
df_tmin_2015['Date'] = df_tmin_2015['Date'].dt.strftime('%m-%d')

df_tmax_2005_2014['Date'] = df_tmax_2005_2014['Date'].dt.strftime('%m-%d')
df_tmax_2015['Date'] = df_tmax_2015['Date'].dt.strftime('%m-%d')

# Group by Date (Month Day) and find the min for TMIN and max for TMAX
tmin_2005_2014 = df_tmin_2005_2014.groupby('Date', as_index=False)['Data_Value'].min()
tmax_2005_2014 = df_tmax_2005_2014.groupby('Date', as_index=False)['Data_Value'].max()

# Merge to align 2015 data with historical data for comparison
tmin_2015_merged = pd.merge(df_tmin_2015, tmin_2005_2014, on='Date', suffixes=('_2015', '_2005_2014'))
tmax_2015_merged = pd.merge(df_tmax_2015, tmax_2005_2014, on='Date', suffixes=('_2015', '_2005_2014'))

# Identify where 2015 data breaks records
tmin_break = tmin_2015_merged[tmin_2015_merged['Data_Value_2015'] < tmin_2015_merged['Data_Value_2005_2014']]
tmax_break = tmax_2015_merged[tmax_2015_merged['Data_Value_2015'] > tmax_2015_merged['Data_Value_2005_2014']]

# Plotting
plt.figure(figsize=(15, 8))

# Plot 2005-2014 highs and lows
plt.plot(tmin_2005_2014.index, tmin_2005_2014['Data_Value'], color='blue', label='Record Low (2005-2014)')
plt.plot(tmax_2005_2014.index, tmax_2005_2014['Data_Value'], color='red', label='Record High (2005-2014)')

# Shade between record highs and lows
plt.fill_between(tmin_2005_2014.index, tmin_2005_2014['Data_Value'], tmax_2005_2014['Data_Value'],
                 color='lightgray', alpha=0.3)

# Overlay 2015 record-breaking points
plt.scatter(tmin_break.index, tmin_break['Data_Value_2015'], color='blue', s=10, label='2015 Record-Breaking Low')
plt.scatter(tmax_break.index, tmax_break['Data_Value_2015'], color='red', s=10, label='2015 Record-Breaking High')

# Labels and aesthetics
plt.title('Record High and Low Temperatures (2005-2014) with 2015 Record-Breaking Days')
plt.xlabel('Day of the Year')
plt.ylabel('Temperature (°C)')
plt.xticks(np.linspace(0, len(tmin_2005_2014.index) - 1, 12), month_abbr[1:], rotation=45)
plt.legend(loc='best')
plt.grid(visible=True, which='both', linestyle='--', linewidth=0.5)

# Display the plot
plt.show()
