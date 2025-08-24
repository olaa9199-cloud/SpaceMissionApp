import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
import datetime

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

    /* CSS for the 'ghost text' effect on birthday inputs */
    /* When no missions are found for the submitted date */
    .birthday-inputs-faded .stNumberInput > label {
        color: #888 !important; /* Grey out the label */
    }
    .birthday-inputs-faded .stNumberInput input { /* Targeting the input element directly */
        color: #888 !important; /* Grey out the input text */
        background-color: #333 !important; /* Slightly darker background to show fading */
        border-color: #555 !important;
    }
    .birthday-inputs-faded .stNumberInput button { /* Grey out +/- buttons */
        color: #888 !important;
        border-color: #555 !important;
    }

    /* When missions ARE found for the submitted date, ensure they are clearly white */
    .birthday-inputs-normal .stNumberInput > label {
        color: white !important;
    }
    .birthday-inputs-normal .stNumberInput input {
        color: white !important;
        background-color: black !important;
        border-color: white !important;
    }
    .birthday-inputs-normal .stNumberInput button {
        color: white !important;
        border-color: white !important;
    }

    </style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'missions_data' not in st.session_state:
    st.session_state.missions_data = pd.DataFrame()
if 'nasa_image_data' not in st.session_state:
    st.session_state.nasa_image_data = {}
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

# Convert the 'Date' column to datetime and then to string for the selectbox
# Also, handle potential errors
sp['Date'] = pd.to_datetime(sp['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
# Get a list of unique, sorted dates to display in the dropdown
available_dates = sorted(sp['Date'].dropna().unique().tolist())

# --- Birthday input section ---
st.subheader("Enter The Date Of The Mission")

# Use a selectbox to show only dates from the dataset
selected_date_str = st.selectbox(
    "Select a Date from the Missions Dataset:",
    options=available_dates,
    key="mission_date_select"
)

# Display status after inputs but before the submit button
if st.session_state.has_missions_for_birthday is not None and st.session_state.submitted:
    if st.session_state.has_missions_for_birthday:
        st.markdown(f'<span class="date-status-found">🎉 Missions found on {st.session_state.selected_date_str}!</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="date-status-not-found">😔 No missions on {st.session_state.selected_date_str}.</span>', unsafe_allow_html=True)


# Submit button logic for birthday
if st.button("Submit Mission Date", key="submit_birthday_button"):
    st.session_state.submitted = True
    
    st.session_state.selected_date_str = selected_date_str

    # Filter missions data using the full date string
    filtered_missions = sp[sp['Date'] == selected_date_str]
    st.session_state.missions_data = filtered_missions
    st.session_state.has_missions_for_birthday = not filtered_missions.empty


# Display Birthday Results (Missions and NASA Image on Birthday) IF submitted
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
