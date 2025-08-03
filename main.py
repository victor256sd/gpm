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
    # INSTRUCTION_LAT_ENCRYPTED = b'gAAAAABojm_FmESpDPXz3RA7rBg67IT8YfH7VG8m0f5abuXoNuG1H_8UT5cM61bux5AcXHiUcYLAc79JeaUBktuUB6PoHbc8KVxcJ1fDvNYtns8bpdwOjYzEZnrbmJZUH5_8X2NSA8igVZka8zGlJUlo88Tm6MMm8hYM397N3LzlIUFethM51Zg='
    # INSTRUCTION_LON_ENCRYPTED = b'gAAAAABojnADPUr62ZYbYBRhlhulPG0Gb68xaWluZjcF-P2Og2jqfO-EvArqjlF9wZvaJTCjZmd-YIKpOoNGugTdzt007M9AsLEMWDmsrhfneWP299XmFedu4aeULPd-T7KRiYNOMT9FNs6jSubgj-22-VdGQbhMTzpwKD_WZpVOZluXBAsg6Hs='

    key = st.secrets['INSTRUCTION_KEY'].encode()
    f = Fernet(key)
    # INSTRUCTION_LAT = f.decrypt(INSTRUCTION_LAT_ENCRYPTED).decode()
    # INSTRUCTION_LON = f.decrypt(INSTRUCTION_LON_ENCRYPTED).decode()
    
    # lat = pandas_ai.run(df, prompt=INSTRUCTION_LAT)
    # lon = pandas_ai.run(df, prompt=INSTRUCTION_LON)

    # data = pd.DataFrame({'lat': lat, 'lon': lon})
    
    # Convert columns to numeric, forcing non-convertible values to NaN
    # data['lat'] = pd.to_numeric(data['lat'], errors='coerce')
    # data['lon'] = pd.to_numeric(data['lon'], errors='coerce')
    
    # Drop rows where conversion failed (so we only keep real coordinates)
    # data = data.dropna(subset=['lat', 'lon'])    
    
    INSTRUCTION_ENCRYPTED = b'gAAAAABojtcIyaYuM7nR6r91Gm40GyCfBf8V4CQOXHO9gIipGVbOfMlw_ISbxEURHVJZWxyGsi7_xZNp26iJ94kL2uqHi7J9YPiMzZmgzTzJN8bUHPgwQkUfSobXVZRlU8w-M8kgxy3gfjAysFsE-uXMv5QBfqN62qErsUjOrlxIppwvlJf1kQ3jeTT7t8LSsjjc6f5qqwRz0Mh3MQL20kOLNcas-8_Lcf3lGfzD_NdKd4y3LHqi3OEJk4ZdpqmdV_ft5a3dt1VKxiy55WD21_b1xd4NKEtz59RcOrKWOXF6bFZfyWf4leU-N5sP7Un8VyUGzzqtbLjjxSNPl4Njj-oWKwzP2HYI6dh7tMDfa6-WBLp55dJiNHTfBYgPwWsfjkECP2KsFbN15r8GgfqRgjh_DfJa5t6teHvfDVWjKez09_If4qu2W21GipuMR6_Ai93PaDUugCAELBztlleT1eIatms2UIQrKC9SUzQMMWaoXRHZnN17JV4lqOtYNyhZ9P2fqznar8-wRbTXLnzpMfKAMu_-wwQO_t7J3wgywLjczk2gjefg3F1Dlcg6VU50AfgFiI0npQUjXu0UBjfIxG3Lnl6rm770JsaaxE5rdiapVOJhuio6WWk8bPPa6aQ2OXrlM8XZST6bEiY0VxQuwOxdue9_WC3lh2vvZpVKVO5cYTwthC7rxeKrdEwDg02E2s7OL8fZiCzOvzA3uvhIJOhX1KWS3tuFxLue_gKqg6mE9NXjpezonv1xgwlHGazmK2zT1U3nmcnlPhECfC3iei2qIlpwlV0mO43NSVWANcPytfuBVdMarA3BKSSjfEuXy2u6nCHNBHNxfeV02VmFFrlaRwdCsE84fCkDwxSNNEGRBLcw7PpjQZGKHQC6IKZn1sxP7MdrhVpUcF6C-Im1XItNrdFFhWJTdmEb-T9H5bbfEWAv6tAxkMQcRPX_qDjmeRJow7rgE-j7bf85wyDJTjZlcqdcjVL8nCvhfMT8U4KD_-2-4eAUEjvcPHL84UonMIW64MXMKfJee0ttIeCWDO1FbQuwnKmw-6UZSKYFa-8jqbZPHEu631aYyLHp8wI568Q5sVv1NDKoDpyx6Q45n51TeUIY3Z-05DmZh6TuJ9FgxmeDRAJGMuTsr7kZq3KAaEy2R_FkSfvl1br0Gr3tED7ySTub1_AoFcwqKTlxHooZ1rxMkXciHFTTvaL47UWlvYwpYngQAB0QEaSnLXtYBpunLvgUue_XXbEeGWk-OzPDv9CZjc4b2PjBhxVhQ0cnYBn5rDeKCj3g_gs-vzPIGqoJkt_Xpc8vPX4DLHNMxJMIE6FxgY-R-Lqjm0Fb8RQVSb3QbC2UcoudLJmE1Ed5s-Zf1yxZn2qKkQO0xNEbxy8Pf6pKvKHwag49xDFkZKrFZG_abL7nRWprF1GXNWjYUKykee4lL8v2NKUTcuByhFyAAPBTs3RmQgMJrIORooxFh73Cx09agzXNw6CHQuH4g-14XlO-XbhzdWMC8yQZSXQ6K5YbmHLJ5cN5pEgnoEYSLD3yvmhbSj97d0E5b94LcOMGB6EKRDxSBQP3dZ3ZfdEuNQHFCFwsdoWqZc2NYJyWzgurK9zON4GqZCMm5AV04aP1O1eQlbYTgknzvV1vMmLoX083InFVrmfH10qpkKQG19GW5btpTSpFXnrgMNVhAfZ8ebiJJf40BbdHIpjylF66exDXNSsxsQV2tvcoZvIdL8vpnALBFRFqd4A_llZLNWv2TSLySeOexNIj8Z55BLGbd0USxHtCY8-5C4EULXDF5LqB3J-Rur3RjgzwO1LStRdXtJej7Trxe2nIXeHjbNBsX7zvuvNRhLtuvXcFulxi7hk1XXE_L1LdrCeyBiP4kgR_3m4iGTA3_6oectCq3CaYfkvPpIJtw0dkXEaCZGmiFFnUNl9J2-7eM4TvS2w_ALR2MmMlxpGck0YnitkvkGTy7dr5Y2Sr4jB-rVXiK8d04NtcER2jWej2hPtybHn1VXoCiXHSgZmtZAkyvDU2QqxPdkgPRP7G4X8eqDEstaF2JEObPqSBLzARPpBcUa8vtxsr1yTXKzz3IH15sXqso-I5NyLghkdN-Ag08D8k10Lo1bYZDgP6f0QChaf_XvAqdsEOln-0dkqpShFqk8NH-_nBl-zFUTIWMzLEtO-6qpBjNroV8_NqA3GkFrR5kOOmGNXQBPlxGa3XzfZhLvmZm57Nos72R0AeGdLKBxt7z4vBeeIgrhI63Im6f6VjIzWotwKdWV3jBqyGlfTgnEK1yKyLL0OxGCtv_9tne1fzWz38OcDIsoCaC87kIN_yvRTJ8AU1j77lkVSopgGGx7V2lD5MvGbaTgPLtKY='
    INSTRUCTION = f.decrypt(INSTRUCTED_ENCRYPTED).decode()
    
    html_data_response = pandas_ai.run(df, prompt=INSTRUCTION)
    
    return html_data_response

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
        doc_ex = st.checkbox("Upload Excel or csv file for mapping", value=True)
                    
    # If the option to upload a document was selected, allow for an upload and then 
    # process it.
    if doc_ex:
        # File uploader for Excel files
        uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"], key="uploaded_file")
        # If a file is uploaded, extract the text and write serialized information to a text file, 
        # give options for further processing, and run assistant to process the information.
        if uploaded_file:
            # Read file, for each row combine column information, create json string, and
            # serialize the data for later processing by the openai model.
            if Path(uploaded_file.name).suffix.lower() == ".xlsx" or Path(uploaded_file.name).suffix.lower() == ".xls":            
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            # Form input and query
            with st.form("doc_form", clear_on_submit=False):
                submit_doc_ex = st.form_submit_button("Map", on_click=disable_button)
                if submit_doc_ex and doc_ex:
                    # Prep data for mapping and map.
                    html_data_response = map_prep(df)
                    html_data = html_data_response.output[1].content[0].text
                    
                    # st.markdown(uploaded_file.name)
                    # with st.spinner('Mapping...'):
                    #     st.map(data)
                    
                    # Use custom HTML and JavaScript to open the file
                    html_code = f"""
                    <script>
                        window.open('{html_data}', '_blank');
                    </script>
                    """

                    st.markdown(html_code, unsafe_allow_html=True)

elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')
