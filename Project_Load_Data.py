import sqlite3
import plotly.express as px
import pandas as pd
import numpy as np


# Connect to Database
filename = "Noise and Position.db"
con = sqlite3.connect(filename)
cursor = con.cursor()

# Print Data
sql = 'SELECT timestamp, longitude, latitude, noise FROM noise'
cursor.execute(sql)
con.close()

# The original code within the Raspberry Pi Pico incorrectly converted the reading by dividing by 63353
# The correct factor to divide by is 65535, which is corrected here:
multFactor = 63353 / 65535

# The original code within the Raspberry Pi Pico incorrectly did not
# convert based on the output voltage of 3 V and input voltage of 3.3 V
# The correct factor to multiply by is 3.3/3, which is corrected here:
voltFactor = 3.3 / 3

# Conversion from decimal degrees to 10 meters
gridFactor = 11113.9
# Other constants for the map
markSize = 5
latFactor = 90
longFactor = 180

# try:
cnn = sqlite3.connect(filename)
df = pd.read_sql(sql, cnn)

df['noise'] = df['noise'] * multFactor * voltFactor

# Remove rows with potentially bad readings
# (close to 30, indicating the sensor was likely disconnected and reading 0)
df = df[df['noise'] >= 33]

to_col = lambda x: np.floor((x + latFactor) * gridFactor).astype(int)
to_row = lambda x: np.floor((x + longFactor) * gridFactor).astype(int)

# Map the latitudes to columns
# Map the longitudes to rows
df['col'] = df.latitude.map(to_col)
df['row'] = df.longitude.map(to_row)
df['longGrid'] = (df['row'] / gridFactor) - longFactor
df['latGrid'] = (df['col'] / gridFactor) - latFactor
df['size'] = markSize

# Group by latitude grid cell and longitude grid cell, then take the median value
df_grouped = df.groupby(['longGrid', 'latGrid', 'size'],
                        as_index=False)['noise'].median().rename(columns={'noise': 'Noise Level (dB)'})

# Reshape dataframe
df_grouped = df_grouped.reset_index()


# Find the max and min lat and long to define map boundaries and calculate zoom
x1 = min(df['longitude'])
x2 = max(df['longitude'])
y1 = min(df['latitude'])
y2 = max(df['latitude'])

# Calculate center point of the map
center = dict(lon=(x1 + (0.5 * (x2 - x1))), lat=(y1 + (0.5 * (y2 - y1))))

# Calculate zoom level
max_bound = max(abs(x2 - x1), abs(y2 - y1)) * 111
zoom = 16 - np.log(max_bound)

# Plot points on map
fig = px.scatter_mapbox(df_grouped, lon=df_grouped['longGrid'], lat=df_grouped['latGrid'], zoom=zoom,
                        color=df_grouped['Noise Level (dB)'], size=df_grouped['size'], opacity=0.8, size_max=15,
                        color_continuous_scale='matter', center=center)

fig.update_traces()
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(showlegend=False)
fig.show()
cnn.close()
