import streamlit as st
import streamlit_authenticator as stauth
import openai
from openai import OpenAI
from openai import AsyncOpenAI
from agents import Agent, ItemHelpers, MessageOutputItem, Runner, FileSearchTool, function_tool, trace
import os
import pandas as pd
import openpyxl
import tiktoken
import json
import time
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
from cryptography.fernet import Fernet
import re
import numpy as np
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

# Start client, thread, create file and add it to the openai vector store, update an
# existing openai assistant with the new vector store, create a run to have the 
# assistant process the vector store.
def generate_response(filename, openai_api_key, model, assistant_id, query_text):    
    # Check file existence.
    if filename is not None:
        # Start client, thread.
        client = OpenAI(api_key=openai_api_key)
        thread = client.beta.threads.create()
        # Start thread.
        client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=query_text
        )
        
        # Create file at openai storage from the uploaded file.
        file = client.files.create(
            file=open(filename, "rb"),
            purpose="assistants"
        )
        
        # Create vector store for processing by assistant.
        vector_store = client.vector_stores.create(
            name="aitam"
        )
        # Obtain vector store and file ids.
        TMP_VECTOR_STORE_ID = str(vector_store.id)
        TMP_FILE_ID = str(file.id)
        # Add the file to the vector store.
        batch_add = client.vector_stores.file_batches.create(
            vector_store_id=TMP_VECTOR_STORE_ID,
            file_ids=[TMP_FILE_ID]
        )        
        # Update Assistant, pointed to the vector store.
        assistant = client.beta.assistants.update(
            assistant_id,
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search":{
                    "vector_store_ids": [TMP_VECTOR_STORE_ID]
                }
            }
        )
        # Create a run to have assistant process the vector store file.
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )
        # Wait on the run to complete, then retrieve messages from the thread.
        run = wait_on_run(client, run, thread)
        messages = get_response(client, thread)
    return messages, TMP_FILE_ID, TMP_VECTOR_STORE_ID, client, run, thread

# Constructed similar to above, exempt no use of the assistant. This calls the 
# llm with a user's query about the vector store. The vector store is re-
# constructed since every action on streamlit runs through the entire code.
# Parts of this function can likely be broken down into other functions. 
# The code might also be restructured to avoid re-building the vector store.
def generate_response_noassist(filename, openai_api_key, model, query_text):    
    # Check file existence.
    if filename is not None:
        # Start client, thread.        
        client = OpenAI(api_key=openai_api_key)
        thread = client.beta.threads.create()
        # Create file at openai storage from the uploaded file.
        file = client.files.create(
            file=open(filename, "rb"),
            purpose="user_data"
        )
        # Create vector store for processing by assistant.
        vector_store = client.vector_stores.create(
            name="aitam"
        )
        # Obtain vector store and file ids.        
        TMP_VECTOR_STORE_ID = str(vector_store.id)
        TMP_FILE_ID = str(file.id)
        # Add the file to the vector store.                        
        batch_add = client.vector_stores.file_batches.create(
            vector_store_id=TMP_VECTOR_STORE_ID,
            file_ids=[TMP_FILE_ID]
        )
        # Get messages from client based on user query of the vector store.
        messages = client.responses.create(
            input = query_text,
            model = model,
            temperature = 1,
            tools = [{
                "type": "file_search",
                "vector_store_ids": [TMP_VECTOR_STORE_ID],
            }]
        )        
    return messages, TMP_FILE_ID, TMP_VECTOR_STORE_ID, client

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

def extract_text_from_excel(uploaded_file):
    output_filename = "temp.txt"
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    df['combined_text'] = df.apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    json_string = df.to_json(path_or_buf=None)
    serialized_data = json.dumps(json_string, indent=4)
    # Write serialized data to a text file.
    with open(output_filename, "w") as file:
        file.write(serialized_data)
    file.close()
    return output_filename

def copy_pdf(uploaded_file):
    # Specify the input and output file paths
    input_pdf_path = uploaded_file
    output_pdf_path = "temp.pdf"
    # Read the input PDF
    reader = PdfReader(input_pdf_path)    
    # Create a writer object to write the copy
    writer = PdfWriter()
    # Add all pages from the input PDF to the writer
    for page in reader.pages:
        writer.add_page(page)
    # Write the copied content to the output file
    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)    
    output_file.close()
    return output_pdf_path

def convert_image_to_pdf(uploaded_file):
    output_file = "temp.txt"
    # Open the image file
    image = Image.open(uploaded_file)
    # Extract text from the image using pytesseract
    extracted_text = pytesseract.image_to_string(image)
    # Write the copied content to the output file
    with open(output_file, "w") as file:
        file.write(extracted_text)
    file.close()
    return output_file
    
# Disable the button called via on_click attribute.
def disable_button():
    st.session_state.disabled = True        

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
    MODEL_LIST = ["gpt-4o-mini", "gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1"] #, "o4-mini"]
    VECTOR_STORE_ID = st.secrets["VECTOR_STORE_ID"]
    MATH_ASSISTANT_ID = st.secrets["MATH_ASSISTANT_ID"]
    MATH_ASSISTANT2_ID = st.secrets["MATH_ASSISTANT2_ID"]
    
    # Set page layout and title.
    st.set_page_config(page_title="Threat AI", page_icon=":spider:", layout="wide")
    st.header(":spider: Threat AI")
    
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    
    # Retrieve user-selected openai model.
    model: str = st.selectbox("Model", options=MODEL_LIST)
    
    # Create advanced options dropdown with upload file option.
    with st.expander("Advanced Options", expanded=True):
        cmte_ex = st.checkbox("Advisory mode - *Consult*")
        lib_ex = st.checkbox("Library mode - *Search*", value=True)
        doc_ex = st.checkbox("Upload Excel, PDF, or image file for examination")
        
    # If there's no openai api key, stop.
    if not openai_api_key:
        st.error("Please enter your OpenAI API key!")
        st.stop()
            
    # If the option to upload a document was selected, allow for an upload and then 
    # process it.
    if doc_ex:
        # File uploader for Excel files
        uploaded_file = st.file_uploader("Choose an Excel, PDF, or image (heif, jpg, png) file", type=["xlsx","pdf","heif","jpg","png"], key="uploaded_file")
        # If a file is uploaded, extract the text and write serialized information to a text file, 
        # give options for further processing, and run assistant to process the information.
        if uploaded_file:
            # Read file, for each row combine column information, create json string, and
            # serialize the data for later processing by the openai model.
            if Path(uploaded_file.name).suffix.lower() == ".xlsx":            
                filename = extract_text_from_excel(uploaded_file)
            elif Path(uploaded_file.name).suffix.lower() == ".pdf":
                filename = copy_pdf(uploaded_file)
            elif Path(uploaded_file.name).suffix.lower() == ".heif" or Path(uploaded_file.name).suffix.lower() == ".jpg" or Path(uploaded_file.name).suffix.lower() == ".png" or Path(uploaded_file.name).suffix.lower() == ".jpeg":
                filename = convert_image_to_pdf(uploaded_file)
            # If there's no openai api key, stop.
            if not openai_api_key:
                st.error("Please enter your OpenAI API key!")
                st.stop()    
            # Form input and query
            with st.form("doc_form", clear_on_submit=False):
                # Create form to process file with the aitam assistant and be able to ask specific
                # questions about the file.
                submit_doc_ex = st.form_submit_button("Standard Examination", on_click=disable_button)
                query_doc_ex = st.text_area("**Custom Queries**")
                submit_doc_ex_form = st.form_submit_button("Submit Query")
                # If there's no openai api key, stop.
                if not openai_api_key:
                    st.error("Please enter your OpenAI API key!")
                    st.stop()
                # Conduct standard aitam eval on the file.
                if submit_doc_ex and doc_ex:
                    query_text = "I need your help analyzing the uploaded document."
                    # Call function to copy file to openai storage, create vector store, and use an 
                    # assistant to eval the file.
                    with st.spinner('Calculating...'):
                        (response, TMP_FILE_ID, TMP_VECTOR_STORE_ID, client, run, thread) = generate_response(filename, openai_api_key, model, MATH_ASSISTANT_ID, query_text)
                    # Write disclaimer and response from assistant eval of file.
                    st.write("*As the Threat AI system continues to be refined. Users should review the original file and verify the summary for reliability and relevance.*")
                    st.write("#### Summary")
                    i = 0
                    for m in response:
                        if i > 0:
                            st.markdown(m.content[0].text.value)
                        i += 1
                    # Reset the button state for standard aitam file eval, and 
                    # delete the file from openai storage and the associated
                    # vector store.
                    submit_doc_ex = False
                    delete_vectors(client, TMP_FILE_ID, TMP_VECTOR_STORE_ID)
                # If the user provides a custom query for the file and submits it, 
                # call different function to use a different assistant to run the 
                # query on the file.

            # Sample data: Latitude and Longitude
            data = pd.DataFrame({
                'lat': [37.7749, 34.0522, 40.7128],
                'lon': [-122.4194, -118.2437, -74.0060]
            })
            
            # Display the map
            st.title("Interactive Map Example")
            st.map(data)

elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')
