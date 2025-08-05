import streamlit as st
import streamlit_authenticator as stauth
import openai
from openai import OpenAI
from openai import AsyncOpenAI
from agents import Agent, ItemHelpers, MessageOutputItem, Runner, FileSearchTool, function_tool, trace
import asyncio
import os
import pandas as pd
import openpyxl
import json
import time
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
from cryptography.fernet import Fernet
# from pandasai import PandasAI
# from pandasai.llm.openai import OpenAI

# Wait until run process completion.
def wait_on_run(client, run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

# Retrieve messages from the thread, including message added by the assistant.
def get_response(client, thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

# Disable the button called via on_click attribute.
def disable_button():
    st.session_state.disabled = True        

# Delete file in openai storage and the vector store.
def delete_vectors(client, TMP_FILE_ID, TMP_VECTOR_STORE_ID):
    # Delete the file and vector store
    deleted_vector_store_file = client.vector_stores.files.delete(
        vector_store_id=TMP_VECTOR_STORE_ID,
        file_id=TMP_FILE_ID
    )
    deleted_vector_store = client.vector_stores.delete(
        vector_store_id=TMP_VECTOR_STORE_ID
    )

# Start client, thread, create file and add it to the openai vector store, update an
# existing openai assistant with the new vector store, create a run to have the 
# assistant process the vector store.
def map_prep(df):
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    assistant_id = st.secrets["MATH_ASSISTANT_ID"]

    llm = OpenAI(api_key=openai_api_key)
    thread = llm.beta.threads.create()

    # Convert DataFrame to JSON string
    df_json = df.to_json(orient="records")

    filename = "df.json"
    # Writing JSON data to a file
    with open(filename, "w") as json_file:
        json.dump(df_json, json_file, indent=4)  
    json_file.close()

    # Start thread.
    query_text = "Use assistant to analyze and generate an html file based on instructions and provided dataframe data in json format."
    llm.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=query_text
    )
    
    # Create file at openai storage from the uploaded file.
    file = llm.files.create(
        file=open(filename, "rb"),
        purpose="assistants"
    )
    
    # # Create vector store for processing by assistant.
    # vector_store = llm.vector_stores.create(
    #     name="fastmap-temp"
    # )
    # # Obtain vector store and file ids.
    # TMP_VECTOR_STORE_ID = str(vector_store.id)
    # TMP_FILE_ID = str(file.id)
    # # Add the file to the vector store.
    # batch_add = llm.vector_stores.file_batches.create(
    #     vector_store_id=TMP_VECTOR_STORE_ID,
    #     file_ids=[TMP_FILE_ID]
    # )        

    # Update Assistant, pointed to the vector store.
    assistant = llm.beta.assistants.update(
        assistant_id,
        tools=[{"type": "code_interpreter"}],
        tool_resources={
            "code_interpreter": {
              "file_ids": [file.id]
            }
        }
        # tools=[{"type": "file_search"}],
        # tool_resources={
        #     "file_search":{
        #         "vector_store_ids": [TMP_VECTOR_STORE_ID]
        #     }
        # }
    )
    # Create a run to have assistant process the vector store file.
    run = llm.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )
    # Wait on the run to complete, then retrieve messages from the thread.
    run = wait_on_run(llm, run, thread)
    messages = get_response(llm, thread)
    
    i = 0
    html_chunks = []
    html_data = ""
    for m in messages:
        if i > 0:
            html_chunks.append(m.content[0].text.value)
        i += 1
    html_data = "".join(html_chunks)
    
    # delete_vectors(llm, TMP_FILE_ID, TMP_VECTOR_STORE_ID)
    return html_data

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
    st.set_page_config(page_title="Fastmap Pro", page_icon=":globe_with_meridians:", layout="wide")
    st.header(":globe_with_meridians: Fastmap Pro")
        
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
                    # Call function to copy file to openai storage, create vector store, and use an 
                    # assistant to eval the file.
                    with st.spinner('Calculating...'):
                        # Prep data for mapping and map.
                        html_data = map_prep(df)
                    
                    # # html_data = html_data_response.choices[0].text.strip() #.output[1].content[0].text
                    # st.markdown(uploaded_file.name)
                    # with st.spinner('Mapping...'):
                    #     st.map(data)
                    
                    # Use custom HTML and JavaScript to open the file
                    html_code = f"""
                    <script>
                        window.open('{html_data}', '_blank');
                    </script>
                    """
                    st.write(html_data)
                    st.markdown(html_code, unsafe_allow_html=True)

elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')
