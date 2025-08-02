import streamlit as st
import streamlit_authenticator as stauth
import os
import pandas as pd
import openpyxl
import time
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
from cryptography.fernet import Fernet
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI
    
# Disable the button called via on_click attribute.
def disable_button():
    st.session_state.disabled = True        

def map_prep(df):
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    llm = OpenAI(api_token=openai_api_key)
    pandas_ai = PandasAI(llm, conversational=False)

    # lat = []
    # lon = []
    INSTRUCTION_LAT_ENCRYPTED = b'gAAAAABojmuMnuZuTfj7RJJETg-yKFv_3Oq1YFsxIjcNgU8x0MAVhKq3nw5EzpFsRDMAksqN1PuIUiTpwaSNkvofRD99fd653-BkDL2xcAl687zE73BE1jD56t26rlevXawB_FsZsBfyuDGN9QpomzaggjB-dbDul_h87rjUXMIyNQwtg6ZHcnmwFrsSHPtARh4f7Z2-y6k-phVht-NR1ZmfbZmvdAZqAjXuCVXc_vT99e6_gCDvcdRpNQBkNxXRFViJn7_bOCtYuCEVQF1Of-ghD8tcvwx2jQ=='
    INSTRUCTION_LON_ENCRYPTED = b'gAAAAABojmvC7e4HqiHk5puQ96HaEPEDhOYgo1Dcpj1j_-EdkE1ylzHdmEcAKkZoZwCl4rMGOfcA3LJhVwuXwQjDfK30P-u5fkpCeDL4pKymnvaRbcmsS5FF7uFbuAccadxN4kj_ANGVfAzxP-2Sfm97fQQjp6WNzvvso1k5n82hOPjLX5YE-n6yFt-b0bwlZ8nkL2OMCZSCEvrmhGFzEtUVc8z-Iz1ipd_d_jnr5hWeCa6Pn3XixJHuFuyFEKgSQaEqNhCsZZbtjDxdw1f53zI1E3J3C-DMYQ=='

    key = st.secrets['INSTRUCTION_KEY'].encode()
    f = Fernet(key)
    INSTRUCTION_LAT = f.decrypt(INSTRUCTION_LAT_ENCRYPTED).decode()
    INSTRUCTION_LON = f.decrypt(INSTRUCTION_LON_ENCRYPTED).decode()
    
    lat = pandas_ai.run(df, prompt="Find the column representing latitude (regardless of its exact name), convert all its values to decimal degrees if needed, and return the result.")
    lon = pandas_ai.run(df, prompt=INSTRUCTION_LON)

    st.write(lat)
    st.write(lon)
    
    data = pd.DataFrame({'lat': lat, 'lon': lon})
    
    # Convert columns to numeric, forcing non-convertible values to NaN
    data['lat'] = pd.to_numeric(data['lat'], errors='coerce')
    data['lon'] = pd.to_numeric(data['lon'], errors='coerce')
    
    # Drop rows where conversion failed (so we only keep real coordinates)
    data = data.dropna(subset=['lat', 'lon'])    
    
    return data

# Definitive CSS selectors for Streamlit 1.45.1+
st.markdown("""
<style>
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    div[data-testid="stStatusWidget"] {
        visibility: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# Load config file with user credentials.
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initiate authentication.
authenticator = stauth.Authenticate(
    config['credentials'],
)

# Call user login form.
result_auth = authenticator.login("main")
    
# If login successful, continue to aitam page.
if st.session_state.get('authentication_status'):
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{st.session_state.get('name')}* !')

    # Model list, Vector store ID, assistant IDs (one for initial upload eval, 
    # the second for follow-up user questions).
    # MODEL_LIST = ["gpt-4o-mini", "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1"] #, "o4-mini"]
    # VECTOR_STORE_ID = st.secrets["VECTOR_STORE_ID"]
    # MATH_ASSISTANT_ID = st.secrets["MATH_ASSISTANT_ID"]
    # MATH_ASSISTANT2_ID = st.secrets["MATH_ASSISTANT2_ID"]
    
    # Set page layout and title.
    st.set_page_config(page_title="Fastmap", page_icon=":globe_with_meridians:", layout="wide")
    st.header(":globe_with_meridians: Fastmap")
        
    # Retrieve user-selected openai model.
    # model: str = st.selectbox("Model", options=MODEL_LIST)
    
    # Create advanced options dropdown with upload file option.
    with st.expander("Analysis Options", expanded=True):
        doc_ex = st.checkbox("Upload Excel or csv file for mapping")
                    
    # If the option to upload a document was selected, allow for an upload and then 
    # process it.
    if doc_ex:
        # File uploader for Excel files
        uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx","csv"], key="uploaded_file")
        # If a file is uploaded, extract the text and write serialized information to a text file, 
        # give options for further processing, and run assistant to process the information.
        if uploaded_file:
            # Read file, for each row combine column information, create json string, and
            # serialize the data for later processing by the openai model.
            if Path(uploaded_file.name).suffix.lower() == ".xlsx":            
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            elif Path(uploaded_file.name).suffix.lower() == ".csv":
                df = pd.read_csv(uploaded_file)
            print(df)
            # Form input and query
            with st.form("doc_form", clear_on_submit=False):
                submit_doc_ex = st.form_submit_button("Map", on_click=disable_button)
                if submit_doc_ex and doc_ex:
                    # Prep data for mapping and map.
                    data = map_prep(df)
                    st.markdown(uploaded_file.name)
                    with st.spinner('Mapping...'):
                        st.map(data)

elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')
