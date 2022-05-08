#!/usr/bin/env python
# coding: utf-8

# In[14]:


# import relevant packages
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import base64
import folium
from streamlit_folium import folium_static
import pyrebase
import datetime
import urllib
import urllib.request
from PIL import Image

st.set_page_config(
    page_title="COVID-19 Dashboard",
    page_icon=":bar_chart:",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Covid-19 Tracker V1.0"
    }
)

firebaseConfig = {
    "apiKey": "AIzaSyBYSwVwuuWe4ZxZpoNuCXWKWfmZXqWh9Lc",
    "authDomain": "pandemic-tracker-1b4e2.firebaseapp.com",
    "databaseURL": "https://pandemic-tracker-1b4e2-default-rtdb.firebaseio.com",
    "projectId": "pandemic-tracker-1b4e2",
    "storageBucket": "pandemic-tracker-1b4e2.appspot.com",
    "messagingSenderId": "755928698748",
    "appId": "1:755928698748:web:ecb56541688d390c905ef9",
    "measurementId": "G-EZCGYK8FM2"
}

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()

path_on_cloud_geo = "states.geojson"
path_on_cloud_case = "us-states.csv"
path_on_cloud_trend = "trend.jpg"

path_local_geo = "states.geojson"
path_local_case = "us-states.csv"
path_local_case = "trend.jpg"


# TODO auto refresh; deploy on aws
image = Image.open('trend.jpg')

url1 = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties-recent.csv"
url2 = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv"

df1 = pd.read_csv(url1)
state_data = pd.read_csv(url2)

if st.sidebar.button("Click to refresh for latest data"):
    df1 = pd.read_csv(url1)
    state_data = pd.read_csv(url2)
    #urllib.request.urlretrieve("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties-recent.csv", "us-counties-recent.csv")
    #urllib.request.urlretrieve("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv", "us-states.csv")

    # upload latest
    # storage.child("us-counties-recent.csv").put("us-counties-recent.csv")
    # storage.child("us-states.csv").put("us-states.csv")

    #storage.child(path_on_cloud_geo).download("", path_local_geo)
    #storage.child(path_on_cloud_case).download("", path_local_case)

    # import data

    #df = pd.read_json("pandemic-tracker-1b4e2-default-rtdb-countyList-export.json")

    #df.to_csv('test.csv', index=False)

    #df = pd.read_csv("test.csv")


st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)

st.markdown("""
<nav class="navbar fixed-top navbar-expand-lg navbar-dark" style="background-color: #3498DB;">
  <a class="navbar-brand" href="https://www.bellevuecollege.edu/" target="_blank">Bellevue College</a>
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>
  <div class="collapse navbar-collapse" id="navbarNav">
    <ul class="navbar-nav">
      <li class="nav-item active">
        <a class="nav-link disabled" href="#">Home <span class="sr-only">(current)</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="https://www.cdc.gov/coronavirus/2019-ncov/whats-new-all.html" target="_blank">News</a>
      </li>
	  <li class="nav-item">
        <a class="nav-link" href="https://covid.cdc.gov/covid-data-tracker/" target="_blank">CDC Tracker</a>
      </li>
    </ul>
  </div>
</nav>
""", unsafe_allow_html=True)

st.write(
    """
# COVID-19 Tracker

Click the header of each column can sort the data. Try **Filters** on the left.

***
""")

st.header("Case Overview")

st.image(image, caption='Recent Trend in Washington, Illinois, California')

#st.subheader("Case Overview")

# st.dataframe(df1)

# filters

st.sidebar.header("Filters:")

state = st.sidebar.multiselect(
    "Select the State:",
    options=df1["state"].unique(),
    default="Washington"
)

df_state_selection = df1.query("state == @state")

county = st.sidebar.multiselect(
    "Select the County:",
    options=df_state_selection["county"].unique(),
    default="King"
    # default=df_state_selection["county"].unique()
)


# date slider

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
start_date = st.sidebar.date_input('Start date', yesterday)
end_date = st.sidebar.date_input('End date', today)

if start_date <= end_date:
    st.sidebar.success('Start date: `%s`\n\nEnd date:`%s`' %
                       (start_date, end_date))
else:
    st.sidebar.error('Error: End date must fall after start date.')


df_selection = df1.query("state == @state & county == @county")

mask = (pd.to_datetime(df_selection['date']) >= pd.to_datetime(start_date)) & (
    pd.to_datetime(df_selection['date']) <= pd.to_datetime(end_date))

df_selection = df_selection.loc[mask]


# filtered cases

st.header("Filtered Cases")

st.write('Data Dimension: ' +
         str(df_selection.shape[0]) + ' rows and ' + str(df_selection.shape[1]) + ' columns.')

st.dataframe(df_selection)

# download csv


def filedownload(df1):
    csv = df1.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="cases.csv">Download CSV File</a>'
    return href


st.markdown(filedownload(df_selection), unsafe_allow_html=True)

# map

state_geo = "states.geojson"


choice = ["cases", "deaths"]
choice_selected = st.selectbox("Select choice", choice)

# state_data.isnull().values.any()

date_max = max(state_data['date'])

#state_data['fips'] = state_data['fips'].fillna(0)
#state_data = state_data[state_data['fips'].notna()]

latest_state_data = state_data[state_data['date'] == date_max]
#latest_state_data_new = latest_state_data.drop(['fips'], axis=1)
#latest_state_data_new['fips'] = latest_state_data['fips'].astype('str')

#latest_state_data['deaths'] = latest_state_data['deaths'].astype('int').astype('str')

m = folium.Map(location=[39, -98], zoom_start=4)

folium.Choropleth(
    geo_data=state_geo,
    name="choropleth",
    data=latest_state_data,
    columns=["fips", choice_selected],  # , choice_selected],
    key_on="feature.properties.STATEFP",
    fill_color="YlGn",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=choice_selected,
).add_to(m)

#folium.features.GeoJson('states.geojson', name="State", popup=folium.features.GeoJsonPopup(fields=["NAME"])).add_to(m)

folium.LayerControl().add_to(m)

folium_static(m, width=700, height=500)

#
#json1 = "county.geojson"
#
#m = folium.Map(location=[39,-98], zoom_start=4)
#
##choice = ["cases", "deaths"]
##choice_selected = st.selectbox("Select choice", choice)
#
# folium.Choropleth(
#    geo_data=json1,
#    name="choropleth",
#    data=df1,
#    columns=["fips", "deaths"],#"GEOID",choice_selected],
#    key_on="feature.properties.GEOID",
#    fill_color="YlGn",
#    fill_opacity=0.7,
#    line_opacity=0.2,
#    #legend_name=choice_selected
# ).add_to(m)
#
#
# folium.features.GeoJson('county.geojson',
#	#name="County", popup=folium.features.GeoJsonPopup(fields=["COUNTY_STATE_NAME"])).add_to(m)
#
# folium.LayerControl().add_to(m)
#
#folium_static(m, width=800, height=500)
#
#
