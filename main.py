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
    
    INSTRUCTION_ENCRYPTED = b'gAAAAABojuL8uRW7W3PblXfiH99IXGswYnYKDqYw6Os7dQslwFGh-fh52N_5cr40htRfvLAPcWg5r1yHZCwNhT8OGpiCYOF5maz1Xp2Ar4mdbWs5BRWy75plrjPdZGAUQ-TCc8m3aizQhwOHRBXes79p79_JqEilgW4PPplf9N1ZL_OVZb4mmiivArC_fX5ga1AkEvgXbvGePNX7M2rtvQBa23aebn5PVSFBrNR45McY87994azDrKy5iSaD6nBkUNjObZEbaeH6M9ib2EtfUtT9Zkq9PYytZ3-z8wl_esObblFsOW0zp_VWhTY47idsSZR-Ahhf4WZ4aoWerCLNEwmFxw0xABd1ZCP1jQZoJtLx71Ufy7WNeacxPyXRNQY-cH2xHmwHYhx9U68IOBlwgj5sb9o5t5qPwwGDBCV74MjhtXRhHySwfjRwDqHK5p_QRE0mvd7Q0hiTi7GVGwphvfjPnn93Gyn-wNwEIBGiPHdmLrr2z79oKDnxNxCBL71kWRe9uBtOxeHzQOrDYepqYdn1-pXBgWGNfg6y6MjTPN1P1e633CNOLGgwAsk-mI9oLsLtecgEaa183YzuV0YSNZLov5-vmtKnEVet1nfUs_g2vWR_NJoJRYGJaury7FRKmMwSCkEbRjD7iWCdijQgvufukE8OokAALkiX9t0RV-JhiwGqeZHsaKhUE_nGKushBdIa5-i7tgACEsT2zmiiri9V2KdnqkBlTSQBhxMatse3WkEHPjEEKVh4oSP86sl-r6IgCMH43HV9_FYwvAb8Y3fLLkXullMnssH0sPtm98jZG1F4V1-B9j5fwiH6CwecC0RQs4FsfZ6ZFBPIPEMPw5rKvBCFcExao0GAoOUhzfbzWUdtx-UuCm8QGtWtWoLpWSo6EwyGGFEWVFV2B68x0tX2hpcoP2hv8Lizo1MVUYaej8gfEXnZWqonRxYvU3UsJ-tlTu3hHgfH_e5K22FNwDa5WZ9BPj83EYfe9Kp8cpYnT0iy7Ps4dhHM9jos_DczOJEcLeVrElmvLeWgiNNoZrP6SRPwBq6P-ztkgtQvPH3cVlOjf7Lv5L5ojug1qNGHYKz67PqzfKVYD9515dT1yG3Z7yujlBMOHKDxCoPH6Fppr1OAAB1OjHaymQnvEymtUAhBGNUl10-wkz_GVz-LV0djOXk4PIX8eU4XpUNf4wue9p3X0REvyqddPdi9gO6uaJ1MZgHAzCTPX6egQkUYqjJmrfMMVauSMO9KNqaIH-Utbf4n9IAm49ATyb1d6CzrAPwid_-0GAFGZieoW7aPSEI20Unf_CDoJBjp9sC1IbZ7ENAItr3g9pcE4HbSBfHrZI43Kl8hcJZbkCIxk3Qy9ikw4S6pG--ao5qJ6yp00_WywmNkIFkL9fW6YJOcCtJw5OMqs4VP5lXx-A_15y3zNW-Nw7CRMkV-nchj_60mXemSy0sAKvLDHJY-ACgpm5uCECoSSVBgp5CbnpBZ2N7Cfvde6y3WYGrWhgQKn5BCdsK4oa_pPL1FagVGk4HBP8CHTYAVexWw6E6KA3CL1gn2gASyczGqFi2dOOOcPciqGIHj2RfHj53d-uIcuytUmy52YUrTPT4RSNv09o_CCjFLfKx2FAlqqIZgpfvFXhrRHof0CncbFSBEe2pO374ze9u7YB-bXWq-Um9-7OF--xnqQDN4fvNuddqCJaGxLuJndMop6KFd_JHFNZUHy_XN5ZQcnUr81uidHZUEsH6X0B9lHn6bPeIpHHF_NcaDfmg4idCQgt4ko4bgEAMj1637TW72tF8kCmFbj7FKa-xNyOP27Et02F9tSk5zT2VpdZzaEGkmWJxMiT_LvcyAE-8BBuK_6zbMwEDIVqzzK3w8XV859_HxcqO-1IrE_r-iOr60L5u4nQF8IPaBKuOUjlzODQjZcn0F0Bxc8r0Q1VzLfmi98xC42_WpfErBNzhH_uniZhq-BthzCG_d6BcapnPqkZ-5I58k7dwnXsqOCIB6DArgnPy3tlLWUkfu-qnT4S_ISdPlcYNJsCvgJt_EsUJUST7TLzU1vSRAbmif79maS1epVtM1i5N_0ft3b2IyRIssMkjAwV4xNFLSX6446Q8sFxkZ3uY28U-aHljTWXq32Fz4wZqaiFTBolsmoIiw4paLdeYqgFZ2HB0yDFUbBvz5rhfnK9wD18kA98f7-Zj9JCSyHN9s0YziYxh5705fVFbwETV3NYMY29yHLCWO704HwBnK-wsvp9j-xZaVXyinj85rK1_PIE7j3kW-zST9RTw-f0l-zZHoYh_LFqD1kfFmBw23eDz-O44Y_-kyjCKVNs2fs05nVDwN52h2UlDJBluX4FgWJx_l7Ubi-P39DcyJgWZk1mkrO7xpBHE1qJyA-HyRz5MukykV2zZc9dZqTeOGargJqVHQCAtU9LbCLJiVKnshi3b2TeU9CnrO'
    INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()
    
    # html_data_response = pandas_ai.run(df, prompt=INSTRUCTION)

    # Convert DataFrame to JSON string
    df_json = df.to_json(orient="records")
    
    with st.spinner('Searching...'):
        # response = llm.responses.create(
        #     instructions = INSTRUCTION,
        #     prompt = f"Here is the dataframe in json format: {df_json}",
        #     model = model,
        #     temperature = 0.6,
        # )
        response = llm.completions.create(
            model=model,
            prompt=INSTRUCTION + f"\nHere is the dataframe in JSON format: {df_json}"
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
                    html_data = html_data_response['choices'][0]['text'].strip() #.output[1].content[0].text
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
