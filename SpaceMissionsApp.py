import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
import datetime
import streamlit.components.v1 as components

# --- Custom Component for Birthday Input ---
_COMPONENT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Birthday Input Component</title>
    <script src="https://unpkg.com/streamlit-component-lib@1.0.0/dist/streamlit-component-lib.js"></script>
    <style>
        /* Base styling for the entire body of the component iframe */
        body {
            font-family: sans-serif;
            margin: 0;
            padding: 0;
            background-color: black; /* Ensure component background matches app */
            color: white; /* Default text color */
        }
        /* Styling for the overall container of the custom date inputs */
        .date-input-container-wrapper {
            display: flex;
            flex-direction: column; /* Stack year, month, day vertically in their own lines */
            gap: 10px; /* Space between each input row */
            margin-bottom: 10px;
        }
        /* Styling for each individual date input row (label + input) */
        .date-input-row {
            display: flex;
            align-items: center;
            gap: 10px; /* Space between label and input */
        }
        .date-input-row label {
            color: white; /* Default label color */
            font-weight: bold;
            min-width: 60px; /* Ensure labels align */
            text-align: right;
        }
        .date-input-row input[type="number"] {
            flex-grow: 1; /* Allow input to take available space */
            max-width: 120px; /* Limit max width for a cleaner look */
            padding: 8px;
            border-radius: 5px;
            border: 1px solid #ccc;
            background-color: black; /* Dark theme */
            color: white; /* White text */
            font-size: 1em;
            transition: border-color 0.3s ease, color 0.3s ease, background-color 0.3s ease;
            -moz-appearance: textfield; /* Hide Firefox number input arrows */
        }
        /* Hide Chrome/Safari number input arrows */
        .date-input-row input[type="number"]::-webkit-outer-spin-button,
        .date-input-row input[type="number"]::-webkit-inner-spin-button {
            -webkit-appearance: none;
            margin: 0;
        }
        .date-input-row input[type="number"]:focus {
            outline: none;
            border-color: #4CAF50;
        }

        /* Styles for when no missions are found (faded state) */
        .date-input-container-wrapper.faded .date-input-row input[type="number"],
        .date-input-container-wrapper.faded .date-input-row label {
            color: #888 !important;
            background-color: #333 !important;
            border-color: #555 !important;
        }
        .date-input-container-wrapper.faded .date-input-row input[type="number"]:focus {
            border-color: #888;
        }
        /* Styles for when missions are found (normal state) */
        .date-input-container-wrapper.normal .date-input-row input[type="number"],
        .date-input-container-wrapper.normal .date-input-row label {
            color: white !important;
            background-color: black !important;
            border-color: white !important;
        }
    </style>
</head>
<body>
    <div id="birthday-input-root" class="date-input-container-wrapper">
        <div class="date-input-row">
            <label for="year-input">Year:</label>
            <input type="number" id="year-input" min="1900" max="{max_year}" value="{initial_year}">
        </div>
        <div class="date-input-row">
            <label for="month-input">Month:</label>
            <input type="number" id="month-input" min="1" max="12" value="{initial_month}">
        </div>
        <div class="date-input-row">
            <label for="day-input">Day:</label>
            <input type="number" id="day-input" min="1" max="31" value="{initial_day}">
        </div>
    </div>
    <script>
        let root;
        let yearInput;
        let monthInput;
        let dayInput;
        let isInitialized = false;
        let componentReadySent = false;
        
        // Helper to format date string
        function formatDate(year, month, day) {
            return `${String(year).padStart(4, '0')}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        }

        // Function to send updated date and validity to Streamlit
        function sendDateToStreamlit() {
            const Streamlit = window.Streamlit;
            if (!Streamlit) {
                console.error("sendDateToStreamlit: Streamlit object not available.");
                return;
            }

            const year = parseInt(yearInput.value);
            const month = parseInt(monthInput.value);
            const day = parseInt(dayInput.value);

            let isValid = true;
            let dateString = null;

            try {
                if (isNaN(year) || isNaN(month) || isNaN(day) || yearInput.value.trim().length === 0 || monthInput.value.trim().length === 0 || dayInput.value.trim().length === 0) {
                    isValid = false;
                } else {
                    const testDate = new Date(year, month - 1, day);
                    if (testDate.getFullYear() !== year || testDate.getMonth() !== month - 1 || testDate.getDate() !== day) {
                        isValid = false;
                    } else {
                        dateString = formatDate(year, month, day);
                    }
                }
            } catch (e) {
                isValid = false;
                console.error("sendDateToStreamlit: Date parsing error in component:", e);
            }
            
            // This is the key fix. The component value is set outside the try-catch block.
            Streamlit.setComponentValue({
                year: year,
                month: month,
                day: day,
                date_str: dateString,
                is_valid: isValid
            });
            Streamlit.setFrameHeight();
        }

        // Function to update the component's UI based on arguments from Streamlit
        function updateComponentUI(args) {
            if (!root || !yearInput || !monthInput || !dayInput) {
                console.warn("updateComponentUI: DOM elements not ready for UI update.");
                return;
            }

            const { initial_year, initial_month, initial_day, max_year, has_missions_for_birthday_status } = args;

            if (parseInt(yearInput.value) !== initial_year) yearInput.value = initial_year;
            if (parseInt(monthInput.value) !== initial_month) monthInput.value = initial_month;
            if (parseInt(dayInput.value) !== initial_day) dayInput.value = initial_day;
            
            yearInput.max = max_year;

            if (has_missions_for_birthday_status === true) {
                root.classList.remove('faded');
                root.classList.add('normal');
            } else if (has_missions_for_birthday_status === false) {
                root.classList.remove('normal');
                root.classList.add('faded');
            } else {
                root.classList.remove('faded');
                root.classList.remove('normal');
            }

            if (window.Streamlit) {
                window.Streamlit.setFrameHeight();
            }
        }

        // This function will be called by Streamlit when it wants to render/rerun the component
        function onStreamlitRerun(event) {
            const Streamlit = window.Streamlit;
            if (!Streamlit) {
                console.error("onStreamlitRerun: Streamlit object not available.");
                return;
            }

            const args = event.detail ? event.detail.args : Streamlit.args;

            if (!isInitialized) {
                root = document.getElementById("birthday-input-root");
                yearInput = root.querySelector("#year-input");
                monthInput = root.querySelector("#month-input");
                dayInput = root.querySelector("#day-input");

                if (!root || !yearInput || !monthInput || !dayInput) {
                    console.error("onStreamlitRerun: DOM elements not found during initialization.");
                    return;
                }

                yearInput.addEventListener('input', sendDateToStreamlit);
                monthInput.addEventListener('input', sendDateToStreamlit);
                dayInput.addEventListener('input', sendDateToStreamlit);
                isInitialized = true;
                console.log("Component DOM elements and listeners initialized.");
            }

            updateComponentUI(args);
            sendDateToStreamlit();
        }

        // --- Main Component Initialization Flow ---
        document.addEventListener('DOMContentLoaded', () => {
            console.log("DOMContentLoaded fired. Preparing component.");

            if (window.Streamlit) {
                const Streamlit = window.Streamlit;
                
                Streamlit.events.addEventListener(Streamlit.LIFECYCLE.AFTER_RERUN, onStreamlitRerun);
                console.log("Streamlit AFTER_RERUN listener attached.");
                
                if (!componentReadySent) {
                    Streamlit.setComponentReady();
                    componentReadySent = true;
                    console.log("Streamlit.setComponentReady() called on DOMContentLoaded.");
                }

                onStreamlitRerun({ detail: { args: Streamlit.args } });
            } else {
                console.error("DOMContentLoaded: Streamlit object not available. Component functionality limited.");
            }
        });
    </script>
</body>
</html>
"""

# Create a Streamlit component function
_my_birthday_input = components.declare_component(
    "my_birthday_input",
    html=_COMPONENT_HTML,
    path=None,
)

# Wrapper function for the custom component to be used in the Streamlit app
def birthday_input_component(initial_year=2000, initial_month=1, initial_day=1, has_missions_for_birthday_status=None, key=None):
    """
    A Streamlit component that provides date input fields (Year, Month, Day)
    and sends changes back to Streamlit. It also visually updates based on
    `has_missions_for_birthday_status` passed from Streamlit.
    """
    return _my_birthday_input(
        initial_year=initial_year,
        initial_month=initial_month,
        initial_day=initial_day,
        max_year=datetime.datetime.now().year,
        has_missions_for_birthday_status=has_missions_for_birthday_status,
        key=key,
        default={
            "year": initial_year,
            "month": initial_month,
            "day": initial_day,
            "date_str": f"{initial_year:04d}-{initial_month:02d}-{initial_day:02d}",
            "is_valid": True
        }
    )

# --- Main Streamlit App Configuration ---
st.set_page_config(layout="wide")
st.title("🚀 Space Missions & Hubble Image")

# General CSS for dark theme and white text (still applies to other Streamlit widgets)
st.markdown("""
    <style>
    .stApp {
        background-color: black;
        color: white;
    }
    .block-container {
        text-align: left;
    }
    h1, h2, h3, h4, h5, h6, label, p, .stMarkdown {
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
        font-size: 1.1em;
    }
    .date-status-not-found {
        color: #888; /* Grey */
        font-weight: bold;
        padding-left: 10px;
        font-size: 1.1em;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'missions_data' not in st.session_state:
    st.session_state.missions_data = pd.DataFrame()
if 'nasa_image_data' not in st.session_state:
    st.session_state.nasa_image_data = {}
if 'selected_date_str' not in st.session_state:
    st.session_state.selected_date_str = ""
if 'has_missions_for_birthday' not in st.session_state:
    st.session_state.has_missions_for_birthday = None

# For separate NASA APOD search
if 'nasa_search_submitted' not in st.session_state:
    st.session_state.nasa_search_submitted = False
if 'separate_nasa_image_data' not in st.session_state:
    st.session_state.separate_nasa_image_data = {}
if 'separate_nasa_date_str' not in st.session_state:
    st.session_state.separate_nasa_date_str = ""

# Load the space missions dataset
url = 'https://raw.githubusercontent.com/olaa9199-cloud/SpaceMissionApp/refs/heads/main/dataset_from_space.CSV'
@st.cache_data
def load_data(data_url):
    df = pd.read_csv(data_url)
    df['Year'] = df['Year'].astype(int)
    df['Month'] = df['Month'].astype(int)
    df['Day'] = df['Day'].astype(int)
    return df

sp = load_data(url)

# --- Birthday input section ---
st.subheader("🎂 Enter your birthday")

# Initialize default values for the custom component if not in session state
if 'bday_component_year' not in st.session_state:
    st.session_state.bday_component_year = 2000
    st.session_state.bday_component_month = 1
    st.session_state.bday_component_day = 1

# Render the custom birthday input component
component_value = birthday_input_component(
    initial_year=st.session_state.bday_component_year,
    initial_month=st.session_state.bday_component_month,
    initial_day=st.session_state.bday_component_day,
    has_missions_for_birthday_status=st.session_state.has_missions_for_birthday,
    key="birthday_date_selector"
)

# Extract values from the component's return. Use .get() with defaults for safety
year_bday = component_value.get("year", st.session_state.bday_component_year)
month_bday = component_value.get("month", st.session_state.bday_component_month)
day_bday = component_value.get("day", st.session_state.bday_component_day)
bday_date_str_from_component = component_value.get("date_str", None)
bday_is_valid_from_component = component_value.get("is_valid", False) 

# Store component values in session state for persistence across reruns
st.session_state.bday_component_year = year_bday
st.session_state.bday_component_month = month_bday
st.session_state.bday_component_day = day_bday


# --- Data fetching and display logic based on component output ---
if bday_is_valid_from_component and bday_date_str_from_component:
    if bday_date_str_from_component != st.session_state.selected_date_str:
        st.session_state.selected_date_str = bday_date_str_from_component
        filtered_missions = sp[(sp['Year'] == year_bday) & (sp['Month'] == month_bday) & (sp['Day'] == day_bday)]
        st.session_state.missions_data = filtered_missions
        st.session_state.has_missions_for_birthday = not filtered_missions.empty
        API_KEY = "yy649GUC0vwwZ2Vxu5DupLUuI9TdigRnBRLSwcHR"
        nasa_url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}&date={st.session_state.selected_date_str}"
        try:
            response = requests.get(nasa_url).json()
            st.session_state.nasa_image_data = response
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching NASA image for birthday: {e}")
            st.session_state.nasa_image_data = {}
    
    if st.session_state.has_missions_for_birthday is not None:
        if st.session_state.has_missions_for_birthday:
            st.markdown(f'<span class="date-status-found">🎉 Missions found on {st.session_state.selected_date_str}!</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="date-status-not-found">😔 No missions on {st.session_state.selected_date_str}.</span>', unsafe_allow_html=True)
else:
    if st.session_state.selected_date_str or (year_bday != st.session_state.bday_component_year or month_bday != st.session_state.bday_component_month or day_bday != st.session_state.bday_component_day):
        st.error("Please enter a valid birthday date.")
    st.session_state.missions_data = pd.DataFrame()
    st.session_state.nasa_image_data = {}
    st.session_state.selected_date_str = ""
    st.session_state.has_missions_for_birthday = None

# Display Birthday Results (Missions and NASA Image on Birthday)
if bday_is_valid_from_component and st.session_state.selected_date_str:
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader(f"🚀 Missions on your Birthday ({st.session_state.selected_date_str})")
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
        st.subheader("🌌 Hubble/NASA Image on your Birthday")
        if "url" in st.session_state.nasa_image_data:
            st.image(st.session_state.nasa_image_data["url"], caption=st.session_state.nasa_image_data.get("title", "Hubble Image"))
            st.write(st.session_state.nasa_image_data.get("explanation", ""))
        else:
            st.warning("⚠️ No image available for this date.")
    with col2:
        st.subheader("🗺️ Launch Locations")
        if not st.session_state.missions_data.empty and "latitude" in st.session_state.missions_data.columns and "longitude" in st.session_state.missions_data.columns:
            map_data = st.session_state.missions_data[['latitude', 'longitude', 'Mission', 'Rocket', 'Location']].copy()
            map_data.dropna(subset=['latitude', 'longitude'], inplace=True)
            if not map_data.empty:
                first_lat = map_data.iloc[0]["latitude"]
                first_lon = map_data.iloc[0]["longitude"]
                m = folium.Map(location=[first_lat, first_lon], zoom_start=4, tiles="CartoDB dark_matter")
                for _, row in map_data.iterrows():
                    folium.Marker(
                        location=[row["latitude"], row["longitude"]],
                        popup=f"<b>Mission:</b> {row['Mission']}<br><b>Rocket:</b> {row['Rocket']}<br><b>Location:</b> {row['Location']}",
                        icon=folium.Icon(color="red", icon="rocket", prefix="fa")
                    ).add_to(m)
                st_folium(m, width=600, height=400)
            else:
                st.info("No valid mission location data for this date to display on the map.")
        else:
            st.info("No location data available for this date.")

# --- Separator ---
st.markdown("---")

# --- Separate NASA APOD search section ---
st.subheader("🌌 Search NASA Astronomy Picture of the Day (APOD)")
nasa_apod_input_cols = st.columns(3)
with nasa_apod_input_cols[0]:
    nasa_year = st.number_input("Year:", min_value=1995, max_value=datetime.datetime.now().year, value=st.session_state.get('nasa_year', datetime.datetime.now().year), key="nasa_year_input")
with nasa_apod_input_cols[1]:
    nasa_month = st.number_input("Month:", min_value=1, max_value=12, value=st.session_state.get('nasa_month', datetime.datetime.now().month), key="nasa_month_input")
with nasa_apod_input_cols[2]:
    nasa_day = st.number_input("Day:", min_value=1, max_value=31, value=st.session_state.get('nasa_day', datetime.datetime.now().day), key="nasa_day_input")
st.session_state.nasa_year = nasa_year
st.session_state.nasa_month = nasa_month
st.session_state.nasa_day = nasa_day
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
