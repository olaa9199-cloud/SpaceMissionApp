import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
import datetime
import wikipediaapi

# Ensure the app uses the wide layout
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
    /* Style for the date status indicator */
    .date-status-found {
        color: #4CAF50; /* Green */
        font-weight: bold;
        padding-left: 10px;
        font-size: 1.1em; /* Make it slightly larger */
    }
    .date-status-not-found {
        color: #888; /* Grey */
        font-weight: bold;
        padding-left: 10px;
        font-size: 1.1em; /* Make it slightly larger */
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'missions_data' not in st.session_state:
    st.session_state.missions_data = pd.DataFrame()
if 'selected_date_str' not in st.session_state:
    st.session_state.selected_date_str = ""
if 'has_missions_for_birthday' not in st.session_state:
    st.session_state.has_missions_for_birthday = None

# New session state variables for separate NASA APOD search
if 'nasa_search_submitted' not in st.session_state:
    st.session_state.nasa_search_submitted = False
if 'separate_nasa_image_data' not in st.session_state:
    st.session_state.separate_nasa_image_data = {}
if 'separate_nasa_date_str' not in st.session_state:
    st.session_state.separate_nasa_date_str = ""


# Load the data once
url='https://raw.githubusercontent.com/olaa9199-cloud/SpaceMissionApp/refs/heads/main/dataset_from_space.CSV'
sp=pd.read_csv(url)

# Convert the 'Date' column to datetime
sp['Date'] = pd.to_datetime(sp['Date'], errors='coerce')

# --- Wikipedia API Setup ---
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

# --- Mission Date input section ---
st.subheader("Enter The Date Of The Mission")

# Use st.date_input for a calendar interface
selected_date = st.date_input(
    "Select a Date:",
    datetime.date(2000, 1, 1),
    min_value=datetime.date(1900, 1, 1),
    max_value=datetime.datetime.now().date(),
    key="mission_date_select"
)

# Display status after inputs but before the submit button
if st.session_state.has_missions_for_birthday is not None and st.session_state.submitted:
    if st.session_state.has_missions_for_birthday:
        st.markdown(f'<span class="date-status-found">🎉 Missions found on {st.session_state.selected_date_str}!</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="date-status-not-found">😔 No missions on {st.session_state.selected_date_str}.</span>', unsafe_allow_html=True)


# Submit button logic for mission search
if st.button("Submit Mission Date", key="submit_mission_button"):
    st.session_state.submitted = True
    
    st.session_state.selected_date_str = selected_date.strftime('%Y-%m-%d')

    # Filter missions data using the selected date object
    filtered_missions = sp[sp['Date'].dt.date == selected_date]
    st.session_state.missions_data = filtered_missions
    st.session_state.has_missions_for_birthday = not filtered_missions.empty


# Display Mission Results and Map IF submitted
if st.session_state.submitted:
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"🚀 Missions on {st.session_state.selected_date_str}")

        if not st.session_state.missions_data.empty:
            for _, row in st.session_state.missions_data.iterrows():
                st.write(f"**Mission:** {row['Mission']}")
                st.write(f"**Status:** {row['MissionStatus']}")
                st.write(f"**Rocket:** {row['Rocket']}")
                st.write(f"**Launch Time:** {row['Time']}")
                st.write(f"**Location:** {row['Location']}")
                st.markdown("---")
            
            # --- Add the summary here in col1 ---
            first_mission_name = st.session_state.missions_data.iloc[0]['Mission']
            st.subheader(f"📜 Summary for {first_mission_name}")
            summary_text = get_mission_summary(first_mission_name)
            st.write(summary_text)

        else:
            st.warning("⚠️ No mission found on this date.")


    with col2:
        st.subheader("🗺️ Launch Locations")

        if not st.session_state.missions_data.empty and \
           "latitude" in st.session_state.missions_data.columns and \
           "longitude" in st.session_state.missions_data.columns:

            map_data = st.session_state.missions_data[['latitude', 'longitude', 'Mission', 'Rocket', 'Location']].copy()
            map_data.dropna(subset=['latitude', 'longitude'], inplace=True)

            if not map_data.empty:
                first_lat = map_data.iloc[0]["latitude"]
                first_lon = map_data.iloc[0]["longitude"]

                m = folium.Map(location=[first_lat, first_lon], zoom_start=4, tiles="CartoDB dark_matter")

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
            else:
                st.info("No valid mission location data for this date to display on the map.")
        else:
            st.info("No location data available for this date.")

st.markdown("---")

# --- Separate NASA APOD search section ---
st.subheader("🌌 Search NASA Astronomy Picture of the Day (APOD)")
nasa_apod_input_cols = st.columns(3)
with nasa_apod_input_cols[0]:
    nasa_year = st.number_input("Year:", min_value=1995, max_value=datetime.datetime.now().year, value=datetime.datetime.now().year, key="nasa_year_input")
with nasa_apod_input_cols[1]:
    nasa_month = st.number_input("Month:", min_value=1, max_value=12, value=datetime.datetime.now().month, key="nasa_month_input")
with nasa_apod_input_cols[2]:
    nasa_day = st.number_input("Day:", min_value=1, max_value=31, value=datetime.datetime.now().day, key="nasa_day_input")

nasa_apod_date_is_valid = False
try:
    datetime.date(nasa_year, nasa_month, nasa_day)
    nasa_apod_date_is_valid = True
except ValueError:
    st.error("Please enter a valid date for NASA APOD search.")

if st.button("Get NASA Image", key="get_nasa_image_button"):
    if nasa_apod_date_is_valid:
        st.session_state.nasa_search_submitted = True
        st.session_state.separate_nasa_date_str = f"{nasa_year:04d}-{nasa_month:02d}-{nasa_day:02d}"

        API_KEY = "yy649GUC0vwwZ2Vxu5DupLUuI9TdigRnBRLSwcHR"
        separate_nasa_url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}&date={st.session_state.separate_nasa_date_str}"
        try:
            response = requests.get(separate_nasa_url).json()
            st.session_state.separate_nasa_image_data = response
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching NASA APOD for {st.session_state.separate_nasa_date_str}: {e}")
            st.session_state.separate_nasa_image_data = {}
    else:
        st.session_state.nasa_search_submitted = False

if st.session_state.nasa_search_submitted:
    st.markdown("---")
    st.subheader(f"NASA Image for {st.session_state.separate_nasa_date_str}")
    if "url" in st.session_state.separate_nasa_image_data:
        st.image(st.session_state.separate_nasa_image_data["url"], caption=st.session_state.separate_nasa_image_data.get("title", "NASA APOD Image"))
        st.write(st.session_state.separate_nasa_image_data.get("explanation", ""))
    else:
        st.warning(f"⚠️ No NASA APOD image available for {st.session_state.separate_nasa_date_str}.")
