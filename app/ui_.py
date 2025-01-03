import json
import os
import base64
from typing import Any
import requests
import streamlit as st
import copy
from config import chatbot_config

########################################################################################################################

api_address = chatbot_config["api_address"]

########################################################################################################################

st.set_page_config(page_title=chatbot_config["page_title"],
                   page_icon=chatbot_config["page_icon"],
                   layout="wide",
                   initial_sidebar_state="auto",
                   menu_items=None)

if "messages" not in st.session_state:
    st.session_state.messages = copy.deepcopy(chatbot_config["messages"])

if "ai_avatar_url" not in st.session_state:
    st.session_state.ai_avatar_url = chatbot_config["ai_avatar_url"]

if "user_avatar_url" not in st.session_state:
    st.session_state.user_avatar_url = chatbot_config["user_avatar_url"]

########################################################################################################################
def download_json_file(data: dict, filename: str):
    """Converts a dictionary into a downloadable JSON file."""
    json_data = json.dumps(data, indent=4)
    b64 = base64.b64encode(json_data.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="{filename}">Scarica {filename}</a>'
    return href

def is_complete_utf8(data: bytes) -> bool:
    """Verifica se `data` rappresenta una sequenza UTF-8 completa."""
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False

def main():

    # Sidebar for file upload and chain configuration
    st.sidebar.header("Upload Document and Configure Chain")

    session_id = st.sidebar.text_input("Session ID")
    file_id = st.sidebar.text_input("File ID")
    description = st.sidebar.text_area("Description (optional)")
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=['pdf', 'txt', 'docx'])

    if st.sidebar.button("Upload and Process Document"):
        if not session_id:
            st.sidebar.error("Please enter a Session ID.")
        elif not file_id:
            st.sidebar.error("Please enter a File ID.")
        elif not uploaded_file:
            st.sidebar.error("Please upload a file.")
        else:
            # Proceed to upload the document
            with st.spinner("Uploading and processing the document..."):
                # Prepare the data
                files = {
                    'uploaded_file': (uploaded_file.name, uploaded_file.read()),
                }
                data = {
                    'session_id': session_id,
                    'file_id': file_id,
                    'description': description,
                }

                upload_document_url = f"http://127.0.0.1:8091/upload_document"

                try:
                    response = requests.post(upload_document_url, data=data, files=files)
                    if response.status_code == 200:
                        st.sidebar.success("Document uploaded and processed successfully.")
                        print("Upload and process response:", response.json())
                    else:
                        st.sidebar.error(f"Failed to upload document: {response.text}")
                        print(f"Failed to upload document: {response.status_code}, {response.text}")
                except Exception as e:
                    st.sidebar.error(f"An error occurred: {e}")
                    print(f"An error occurred during upload: {e}")

            # Then execute the chain configuration endpoint
            with st.spinner("Configuring and loading the chain..."):
                configure_chain_url = f"http://127.0.0.1:8091/configure_and_load_chain/?session_id={session_id}"
                try:
                    response = requests.post(configure_chain_url)
                    if response.status_code == 200:
                        st.sidebar.success("Chain configured and loaded successfully.")
                        print("Configure chain response:", response.json())
                    else:
                        st.sidebar.error(f"Failed to configure chain: {response.text}")
                        print(f"Failed to configure chain: {response.status_code}, {response.text}")
                except Exception as e:
                    st.sidebar.error(f"An error occurred: {e}")
                    print(f"An error occurred during chain configuration: {e}")

    st.sidebar.markdown("---")

    st.sidebar.header("Download Workflows")

    collection_name = st.sidebar.text_input("Collection Name (for all workflows)")

    if st.sidebar.button("Download Last Workflow"):
        try:
            get_last_workflow_url = f"http://127.0.0.1:8091/get_last_workflow?session_id={session_id}"
            response = requests.get(get_last_workflow_url)
            if response.status_code == 200:
                workflow_data = response.json()
                st.sidebar.markdown(download_json_file(workflow_data, "last_workflow.json"), unsafe_allow_html=True)
            else:
                st.sidebar.error(f"Failed to retrieve last workflow: {response.text}")
        except Exception as e:
            st.sidebar.error(f"An error occurred: {e}")

        st.sidebar.markdown("---")

    #if st.sidebar.button("Download All Workflows"):
    #    try:
    #        get_all_workflows_url = f"http://127.0.0.1:8091/get_all_workflows?collection_name={collection_name}"
    #        response = requests.get(get_all_workflows_url)
    #        if response.status_code == 200:
    #            workflows_data = response.json()
    #            st.sidebar.markdown(download_json_file(workflows_data, "all_workflows.json"), unsafe_allow_html=True)
    #        else:
    #            st.sidebar.error(f"Failed to retrieve all workflows: {response.text}")
    #    except Exception as e:
    #        st.sidebar.error(f"An error occurred: {e}")


    # Main chat interface
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message(message["role"], avatar=st.session_state.user_avatar_url):
                st.markdown(message["content"])
        else:
            with st.chat_message(message["role"], avatar=st.session_state.ai_avatar_url):
                st.markdown(message["content"])

    if prompt := st.chat_input("Scrivi qualcosa"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        #####################################################################
        if len(st.session_state.messages) > 10:
            st.session_state.messages = st.session_state.messages[-10:]
        #####################################################################

        with st.chat_message("user", avatar=st.session_state.user_avatar_url):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=st.session_state.ai_avatar_url):
            message_placeholder = st.empty()
            s = requests.Session()
            full_response = ""
            url = f"{api_address}/chains/stream_events_chain"
            payload = {
                "chain_id": f"{session_id}-workflow_generation_chain",
                "query": {
                    "input": prompt,
                    "chat_history": st.session_state.messages
                },
                "inference_kwargs": {},
            }

            non_decoded_chunk = b''
            with s.post(url, json=payload, headers=None, stream=True) as resp:
                for chunk in resp.iter_content():
                    if chunk:
                        # Aggiungi il chunk alla sequenza da decodificare
                        non_decoded_chunk += chunk
                        print(chunk)
                        # Decodifica solo quando i byte formano una sequenza UTF-8 completa
                        if is_complete_utf8(non_decoded_chunk):
                            decoded_chunk = non_decoded_chunk.decode("utf-8")
                            full_response += decoded_chunk
                            message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
                            non_decoded_chunk = b''  # Svuota il buffer

            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

########################################################################################################################

main()
