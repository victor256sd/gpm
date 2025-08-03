import streamlit as st
import streamlit_authenticator as stauth
import openai
from openai import OpenAI
import os
import pandas as pd
import openpyxl
import time
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
from cryptography.fernet import Fernet
# from pandasai import PandasAI
# from pandasai.llm.openai import OpenAI

# Disable the button called via on_click attribute.
def disable_button():
    st.session_state.disabled = True        

def map_prep(df):
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    llm = OpenAI(api_key=openai_api_key)
    # pandas_ai = PandasAI(llm, conversational=False)

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
    
    INSTRUCTION_ENCRYPTED = b'gAAAAABojt3HBuPyGlENM66GfOraZ9Np_Wq9nittsRk0nurBClZDD88i6kK2YhBC18lIqVXDbZx3eDi7-QaXt-mVbNiSo68r5uVTMFc8Tj8PIGN3aZCvGWosg4rCTmaS2vUJKxz25WaCUQ1I10Cy4nGfAhQBcBEBX9sEGWlYNWEhQ_A-WPqS02aE5BvVXWQsNnG3QcNx_nk1UqVhlu5k5-2sCUX6AfGYNDzvBAoZwz_Kj1WoCEDOROdDsI07fTC3BzHoe6kMwk0_wweetbE3Cv_sTpl8P3q2qSdP-2X8mRwej0p4rSAeJJrrA1kn7QxnP7vVJWpeuBjsCBgc-WSovauxANe8f695CnXgGsbu5ZJUhiF7KDpwQg_I-D4oKuTmqjBnx-gcKo_dxx-4MLRg40MbnYgaCCa-wJy53rhzhTWbvLKfU3pLyLJUEFgaZk5H6Hl0eE3c1EISrN7Di9_nnRyFX7GaPhcQE0qtwpOiG95_heC8fFdFS1ooNa2JNciaQG4orUXrSu0VaTukQqJ8NorVqX1QYlrPSW95i7lQ9kHogeI4kcYsfM4McPL0UfTSzcPqcMATnc_YanncbgaHPPSGRDqbZcxS2MMDVmjROdRnGvhpJrtGcgyPHa15m0kSZElPJHd_ZRSmnib7mt8sBq62gXKYCyPnMqzRmboy_0Ek21SBfXRm5cMaYGpQAzmKEdoWgSNFTLtb51SPmQqW9j1ifkoANz2Wfc4hH6_HKbLLr1TmF7N5FIAKT0mMXVAnNln-Beb24GdOZ3kUTvmPjAL3OhLkMFHDu2SfcxcsPTZHIBVrNWi0JcvHZJsG0SnOo1fXKkVMrJl_urIhGnB3nJbSjE42c3PjzL2tGwQ8VnMALNi_USZIpaubzdgAocKG8d8sw92B8PPZ6Tpr5tGSAAtBtXwqZwPuss067gbaopAZYeyyhvn8epg2B7m_J3S6FQJhh5l-J4lRRU62GcSmgncSneKfd5021dBCk72mhHLBhkR9xsqQMwkqqQYio6cMntxqxCFaA1Z-_B6O_ovSYDtxaKpKJ3DcDTv57MJxSdjzld6RQHdfkIAVVChrLSoZUHJDH4qRe9ZOSfpPya_i7QowDsjMsxo6x4aU23MA15k7v_-1xoPvhIk9bNhUTs6uIMviwq3vlRjGgqNB-1A8bFe-aLGjPWcNRp5WChfTc_bVOoQsjmfRGhyCtD4Zb-9ita9hlFqJFHapNsbd0JFcBbwGuuOYfm8MmR-9OV2-sU-oBG2R3MZ9_ZFOYOuO1S5EwKZftH6YrSl3z1jCYqlRTAUplqR1evVbmBfHpBGCeptE9bZq--2t0n7zaKERAOz-VD8qiMlMwXSj3FmfNvvX7pxl1ww_cdSk3BV-ugpDI_TydeUkTAFqFyQw-mwfUNtbnKOFZzlrBpTggg7Ux4YR3M_G9gmSOhaT_uRsqaQM2R4p9eJ-vp67y7jYhqBV8qwcRj9ZyaOBPtEhRP7LzvlYjZsAjyK8n1BWvEQijVLeTBCIxvd-Jj0ZnngJqR34HQDK0nGoWDje9C3Rgs1WAB6ckISWutbHnO6nP5abNKNTxTokONGMgBccogQhZANhle6ALUcEEvupQw-Fmlu8eNuqE2tPNnpfB0Cat1Oil1izfWG1U3F88ornTK1AwrYAB4fIlh-wqXa0hym1Mjewyrhy8Lo9JxonNZF7DqGFh1xt3-ouNt9S7Y9AWdwMHyNzAt5e2YLFpyEDzBE1w1p4dPvnwgbO2VfrvGRacww2FcSlSdI-rfD08HQsOf1-KzP2opu2Y7SyVFO6BklIDSSkQWkFBKoixzyOxwzF2W8oHk__igpzxXB4vWeVlbQxzMGS3rufubZWFJm_nty1iHWzfpkrJzsP8WAZnIUqRBAeGirNn6S8wb89CqRwID86BCFQNWsbenCO7jR38jTZ'
    INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()
    
    # html_data_response = pandas_ai.run(df, prompt=INSTRUCTION)

    # Convert DataFrame to JSON string
    df_json = df.to_json(orient="records")
    
    with st.spinner('Searching...'):
        response = llm.responses.create(
            instructions = INSTRUCTION,
            prompt = f"Here is the dataframe in json format: {df_json}",
            model = model,
            temperature = 0.6,
        )
    
    return response

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
    MODEL_LIST = ["gpt-4o-mini"] #, "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1"] #, "o4-mini"]
    # VECTOR_STORE_ID = st.secrets["VECTOR_STORE_ID"]
    # MATH_ASSISTANT_ID = st.secrets["MATH_ASSISTANT_ID"]
    # MATH_ASSISTANT2_ID = st.secrets["MATH_ASSISTANT2_ID"]
    
    # Set page layout and title.
    st.set_page_config(page_title="Fastmap", page_icon=":globe_with_meridians:", layout="wide")
    st.header(":globe_with_meridians: Fastmap")
        
    # Retrieve user-selected openai model.
    model: str = st.selectbox("Model", options=MODEL_LIST)
    
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
