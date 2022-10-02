#!/usr/bin/python3

import pandas as pd
df = pd.read_csv('wigle.csv')

import plotly.express as px
fig = px.density_mapbox(df,
                        lat = 'trilat',
                        lon = 'trilong',
                        radius = 7,
                        center = dict(lat = 0, lon = 180),
                        zoom = 1,
                        hover_name = 'ssid',
                        mapbox_style = 'stamen-terrain',
                        title = "WiGLE Observations")
fig.show()
