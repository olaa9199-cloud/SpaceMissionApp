#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import streamlit as st
import requests
from streamlit_folium import st_folium
import folium
import wikipediaapi


# In[2]:


url='https://raw.githubusercontent.com/olaa9199-cloud/SpaceMissionApp/refs/heads/main/dataset_from_space.CSV'
sp=pd.read_csv(url)


# In[5]:


wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent="SpaceMissionsApp/0.1 (contact: olaa9199@gmail.com)"
)

def get_mission_summary(mission_name, max_chars=500):
    page = wiki_wiki.page(mission_name)
    if not page.exists():
        return "No summary found."
    
    summary = page.summary
    if len(summary) <= max_chars:
        return summary
    
    
    cut = summary[:max_chars].rsplit('.', 1)[0] + '.'
    return cut


# In[ ]:


import datetime 

st.set_page_config(layout="wide")

st.title("🚀 Space Missions & Hubble Image")

# CSS for dark theme and white text
st.markdown("""
    <style>
    .stApp {
        background-color: black;
        color: white;
    }
    .block-container {
        text-align: left;
    }
    h1, h2, h3, h4, h5, h6, label, p, .stMarkdown, .css-1lcbmhc, .stNumberInput {
        color: white !important;
    }
    /* Specific styling for the submit button */
    .stButton>button {
        background-color: #4CAF50; /* Green */
        color: white;
        padding: 10px 24px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
# These variables will save the application's state between reruns
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'missions_data' not in st.session_state:
    st.session_state.missions_data = pd.DataFrame()
if 'nasa_image_data' not in st.session_state:
    st.session_state.nasa_image_data = {}
if 'selected_date_str' not in st.session_state:
    st.session_state.selected_date_str = ""


try:
    # Attempt to use the existing 'sp' if defined.
    # If not, create a placeholder for the example to run.
    _ = sp # This will raise NameError if sp is not defined
except NameError:
    # Placeholder data - REMOVE THIS BLOCK IF 'sp' IS ALREADY LOADED IN YOUR APP
    sp_placeholder_data = {
        'Year': [2000, 2000, 2001, 2001, 2000, 2005],
        'Month': [1, 1, 2, 3, 5, 8],
        'Day': [1, 15, 1, 10, 10, 26],
        'Mission': ['Mars Pathfinder', 'ISS Resupply-1', 'Hubble Servicing-3B', 'Soyuz TM-32', 'STS-101', 'Discovery STS-114'],
        'MissionStatus': ['Success', 'Success', 'Success', 'Success', 'Success', 'Success'],
        'Rocket': ['Delta II', 'Soyuz-U', 'Discovery', 'Soyuz-FG', 'Atlantis', 'Discovery'],
        'Time': ['10:00:00', '15:30:00', '08:00:00', '12:00:00', '06:00:00', '10:39:00'],
        'Location': ['Cape Canaveral', 'Baikonur Cosmodrome', 'Kennedy Space Center', 'Baikonur Cosmodrome', 'Kennedy Space Center', 'Kennedy Space Center'],
        'latitude': [28.3922, 45.9653, 28.5623, 45.9653, 28.5623, 28.5623],
        'longitude': [-80.6077, 63.3052, -80.6489, 63.3052, -80.6489, -80.6489]
    }
    sp = pd.DataFrame(sp_placeholder_data)
    st.info("Note: Placeholder data for 'sp' is being used. Please ensure your actual data is loaded for the app to function correctly.")


# Birthday input
st.subheader("🎂 Enter your birthday")
col_date_input_1, col_date_input_2, col_date_input_3 = st.columns(3)
with col_date_input_1:
    year = st.number_input("Year:", min_value=1900, max_value=datetime.datetime.now().year, value=2000, key="year_input")
with col_date_input_2:
    month = st.number_input("Month:", min_value=1, max_value=12, value=1, key="month_input")
with col_date_input_3:
    day = st.number_input("Day:", min_value=1, max_value=31, value=1, key="day_input")

# Basic date validation
date_is_valid = False
try:
    datetime.date(year, month, day)
    date_is_valid = True
except ValueError:
    st.error("Please enter a valid date.")


# Submit button logic
if st.button("Submit", key="submit_button"):
    if date_is_valid:
        st.session_state.submitted = True
        st.session_state.selected_date_str = f"{year:04d}-{month:02d}-{day:02d}"

        # Filter missions data
        st.session_state.missions_data = sp[(sp['Year'] == year) & (sp['Month'] == month) & (sp['Day'] == day)]

        # Fetch NASA APOD image
        API_KEY = "yy649GUC0vwwZ2Vxu5DupLUuI9TdigRnBRLSwcHR" # Ensure this API key is valid
        nasa_url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}&date={st.session_state.selected_date_str}"
        try:
            response = requests.get(nasa_url).json()
            st.session_state.nasa_image_data = response
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching NASA image: {e}")
            st.session_state.nasa_image_data = {}
    else:
        st.session_state.submitted = False # Do not display results if the date is invalid

# Display results if submitted
if st.session_state.submitted:
    st.markdown("---") # Separator for better readability

    # Layout: two columns for missions/image and map
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"🚀 Missions on {st.session_state.selected_date_str}")

        if not st.session_state.missions_data.empty:
            for _, row in st.session_state.missions_data.iterrows():
                st.write(f"**Mission:** {row['Mission']}")
                st.write(f"**The Company:** {row['Company']}")
                st.write(f"**Status:** {row['MissionStatus']}")
                st.write(f"**Rocket:** {row['Rocket']}")
                st.write(f"**Launch Time:** {row['Time']}")
                st.write(f"**Location:** {row['Location']}")
                st.markdown("---")
        else:
            st.warning("⚠️ No mission found on this date.")

        # --- Hubble / NASA Image ---
        st.subheader("🌌 Hubble/NASA Image for this day")
        if "url" in st.session_state.nasa_image_data:
            st.image(st.session_state.nasa_image_data["url"], caption=st.session_state.nasa_image_data.get("title", "Hubble Image"))
            st.write(st.session_state.nasa_image_data.get("explanation", ""))
        else:
            st.warning("⚠️ No image available for this date.")

    with col2:
        st.subheader("🗺️ Launch Locations")

        if not st.session_state.missions_data.empty and \
           "latitude" in st.session_state.missions_data.columns and \
           "longitude" in st.session_state.missions_data.columns:

            # Create a copy to avoid SettingWithCopyWarning
            map_data = st.session_state.missions_data[['latitude', 'longitude', 'Mission', 'Rocket', 'Location']].copy()

            # Filter out rows with NaN latitude/longitude to prevent map errors
            map_data.dropna(subset=['latitude', 'longitude'], inplace=True)

            if not map_data.empty:
                # First point to zoom in
                first_lat = map_data.iloc[0]["latitude"]
                first_lon = map_data.iloc[0]["longitude"]

                
                m = folium.Map(location=[first_lat, first_lon], zoom_start=4, tiles="CartoDB dark_matter") # Use darker map tiles

                
                for _, row in map_data.iterrows():
                    folium.Marker(
                        location=[row["latitude"], row["longitude"]],
                        popup=f"""
                        <b>Mission:</b> {row['Mission']}<br>
                        <b>Rocket:</b> {row['Rocket']}<br>
                        <b>Location:</b> {row['Location']}
                        """,
                        icon=folium.Icon(color="red", icon="rocket", prefix="fa")
                    ).add_to(m)

                
                st_folium(m, width=600, height=400)
                
                mission_name = map_data.iloc[0]["Mission"]
                summary = get_mission_summary(mission_name)
                st.markdown(f"**Mission Description:** {summary}")
            else:
                st.info("No valid mission location data for this date to display on the map.")
        else:
            st.info("No location data available for this date.")

