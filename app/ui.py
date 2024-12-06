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

if "chat_history" not in st.session_state:
    st.session_state.chat_history = copy.deepcopy(chatbot_config["messages"])

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

def generate_response(prompt, session_id, auto_generated=False):
    """Handles generating a response based on a prompt."""
    chain_id = f"{session_id}-workflow_generation_chain"

    # Show the user message in the chat only if it's not auto-generated
    if not auto_generated:
        with st.chat_message("user", avatar=st.session_state.user_avatar_url):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

    if auto_generated:
        st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar=st.session_state.ai_avatar_url):
        message_placeholder = st.empty()
        s = requests.Session()
        full_response = ""
        url = f"{api_address}/chains/stream_events_chain"
        payload = {
            "chain_id": chain_id,
            "query": {
                "input": prompt,
                "chat_history": st.session_state.chat_history[-20:] if len(st.session_state.chat_history) > 20
                else st.session_state.chat_history
            },
            "inference_kwargs": {},
        }

        non_decoded_chunk = b''
        with s.post(url, json=payload, headers=None, stream=True) as resp:
            for chunk in resp.iter_content():
                if chunk:
                    non_decoded_chunk += chunk
                    if is_complete_utf8(non_decoded_chunk):
                        decoded_chunk = non_decoded_chunk.decode("utf-8")
                        full_response += decoded_chunk
                        message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
                        non_decoded_chunk = b''  # Clear buffer

        message_placeholder.markdown(full_response)

    # Add assistant's response to chat history if not auto-generated
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.chat_history.append({"role": "assistant", "content": full_response})

    return full_response

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

    # Main chat interface
    previus_type = None
    for message in st.session_state.messages:

        if message["role"] == "user" and previus_type != "user":
            with st.chat_message(message["role"], avatar=st.session_state.user_avatar_url):
                st.markdown(message["content"])
        elif message["role"] != "user":
            with st.chat_message(message["role"], avatar=st.session_state.ai_avatar_url):
                st.markdown(message["content"])
        previus_type = message["role"]

    if prompt := st.chat_input("Scrivi qualcosa"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        generate_response(prompt, session_id)

    if st.sidebar.button("Genera Workflows", use_container_width=True):
        if session_id:
            st.sidebar.success("Generazione workflows in corso...")
            generate_workflows(session_id)
        else:
            st.sidebar.error("Per favore, inserisci un Session ID valido.")

    st.sidebar.markdown(
        """
        <div style="text-align: center; margin-top: 20px; font-size: 12px; color: black;">
            &copy; 2024 Teatek s.p.a. Tutti i diritti riservati.
        </div>
        """,
        unsafe_allow_html=True
    )


def generate_workflows(session_id):
    """Generates a report with predefined messages."""

    max_iterations = 20
    grado_di_scomposizione = "Alto"

    message_0 = f"osserva e analizza il docuemnto fornito, dunque ipotizza tutte le workflow che si possono creare (senza crearle) e associa ad esse i contenuti a cui fare riferimento (citando pagine di docuemnti e immagini contenute in essi) per crearle successivamente in dettaglio (le creerai nei prossimi messaggi). queste direttive sintentiche verranno usate dopo per sviluppare sequenzialmente i workflow dettalgiati. concentrati solo sulle workflow di configurazione per un massimo di {max_iterations}, inoltre assicurti di scrivere le proposte di workflow in lista numerata."

    agent_response_0 = generate_response(message_0, session_id, auto_generated=True)

    is_terminated = False
    cnt = 0
    while not is_terminated and cnt <= max_iterations:
        cnt += 1

        messages = [
            # sostiuire ttcontrol con versione generale (riga 1) (valore sostituito ---> grado_di_scomposizione)
            f"""workflow da generare: {message_0} --- genera tutte le workinstruction dettagliate e complete per tutti i flussi definiti Nei docuemnti forniti in input.  
            Inidvidua il prossimo workflow da generare workflows da in ordine di apparizione dei contenuti dal numero 1 al numero N, genera workflow successivo a quello precedentemente generato. In questa fase dovrai generare solo un workflows ( ossia il numero {cnt}) e le sue istruzioni, il successivo workflow sarà poi generato al messaggio successivo, e solo una volta creati tutti i workflows programmati allora dovrai generare stringa di termianzione.
            Dovrai scomporre ogni workflow nel numero di sottotask adatto (tendi a massimizzarlo). Crea workflow dettalgiato e salvalo nel db. 
            Quando crei un workflow mostralo sempre all'utente in formato json. Dovrai mostrare in ogni messaggio una sola rappresnetazione json dettalgiata del workflow.
            Dovai generare workflow scompoenndoli in sottotask con un grado di scomposizione {grado_di_scomposizione}.
            ATTENIONE: Nel caso in cui invece hai già generato tutti i work flow descritti dal messaggio iniziale allora genera la seguente stringa per porre fien all'iterazione '<command=TERMINATION| TRUE |command=TERMINATION>'.""",
        ]

        for message in messages:
            # Use auto_generated=True to avoid duplicating messages in chat history
            agent_response = generate_response(message, session_id, auto_generated=True)
            if "<command=TERMINATION| TRUE |command=TERMINATION>" in agent_response:
                is_terminated = True
                break


main()

