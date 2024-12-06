import base64
import time

from starlette.datastructures import UploadFile as StarletteUploadFile
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Query, Body, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import httpx
import uuid
from fastapi.middleware.cors import CORSMiddleware
import requests
import random
import json
from starlette.responses import StreamingResponse
from io import BytesIO
from app.utilities import get_system_message

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permetti tutte le origini
    allow_credentials=True,
    allow_methods=["*"],  # Permetti tutti i metodi (GET, POST, OPTIONS, ecc.)
    allow_headers=["*"],  # Permetti tutti gli headers
)


class WorkflowInputFile(BaseModel):
    id_file: str = Field(..., description="Identificativo univoco del file")
    content_base64: str = Field(..., description="Contenuto del file in formato Base64")
    description: Optional[str] = Field(None, description="Descrizione opzionale del file")


class GenerateWorkflowsInput(BaseModel):
    files: List[WorkflowInputFile] = Field(..., description="Lista di file in input")
    prompt: str = Field(..., description="Prompt per la generazione dei workflow")

# Carica la configurazione dal file config.json
with open("config.json") as config_file:
    config = json.load(config_file)

NLP_CORE_SERVICE = config["nlp_core_service"]
MONGO_SERVICE_URL = config["mongodb_service"]
openai_api_keys = config["openai_api_keys"]


# Models for handling requests and responses
class ContextMetadata(BaseModel):
    path: str
    custom_metadata: Optional[Dict[str, Any]] = None


class FileUploadResponse(BaseModel):
    file_id: str
    contexts: List[str]


# Funzione per selezionare una chiave API casuale
def get_random_openai_api_key():
    return random.choice(openai_api_keys)


# Helper function to communicate with the existing API
async def create_context_on_server(context_path: str, metadata: Optional[Dict[str, Any]] = None):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{NLP_CORE_SERVICE}/data_stores/create_directory",
            data={
                "directory": context_path,
                "extra_metadata": metadata and json.dumps(metadata)
            }
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()

async def delete_context_on_server(context_path: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{NLP_CORE_SERVICE}/data_stores/delete_directory/{context_path}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()

async def list_contexts_from_server():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{NLP_CORE_SERVICE}/data_stores/directories")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()


async def upload_file_to_contexts_(file: UploadFile, contexts: List[str],
                                  file_metadata: Optional[Dict[str, Any]] = None):
    file_uuid = str(uuid.uuid4())  # Generate a UUID for the file
    file_content = await file.read()  # Read the file content once and reuse it

    contexts = contexts[0].split(',')

    async with httpx.AsyncClient() as client:
        responses = []
        # Sequentially upload the file to each context
        for context in contexts:
            # Ensure that each context is handled separately and not concatenated
            data = {
                "subdir": context,  # Here, context is passed as a single string, not a concatenation
                "extra_metadata": json.dumps({"file_uuid": file_uuid, **(file_metadata or {})}),
            }
            files = {"file": (file.filename.replace(" ", "_"), file_content, file.content_type)}

            # Make the POST request to upload the file to the current context
            response = await client.post(f"{NLP_CORE_SERVICE}/data_stores/upload", data=data, files=files)

            # Log and handle errors
            if response.status_code != 200:
                print(
                    f"Error uploading to {context}. Status Code: {response.status_code}. Response content: {response.content}")

                try:
                    error_detail = response.json()
                except ValueError:
                    raise HTTPException(status_code=response.status_code, detail=f"Error: {response.text}")

                raise HTTPException(status_code=response.status_code, detail=error_detail)

            # Collect response data for successful uploads
            try:
                responses.append(response.json())
            except ValueError:
                raise HTTPException(status_code=500, detail="Received invalid JSON response from the server")

        # Return the collected responses with file UUID and associated contexts
        return {"file_id": file_uuid, "contexts": contexts}


async def upload_file_to_contexts(file: UploadFile,
                                  contexts: List[str],
                                  file_metadata: Optional[Dict[str, Any]] = None):

    file_uuid = str(uuid.uuid4())  # Generate a UUID for the file
    file_content = await file.read()  # Read the file content once and reuse it

    contexts = contexts[0].split(',')
    timeout_settings = httpx.Timeout(600.0, connect=600.0, read=600.0, write=600.0)
    async with httpx.AsyncClient() as client:
        responses = []
        # Sequentially upload the file to each context
        for context in contexts:
            # Upload the file
            data = {
                "subdir": context,
                "extra_metadata": json.dumps({"file_uuid": file_uuid, **(file_metadata or {})}),
            }
            files = {"file": (file.filename.replace(" ", "_"), file_content, file.content_type)}

            # Make the POST request to upload the file to the current context
            response = await client.post(f"{NLP_CORE_SERVICE}/data_stores/upload", data=data, files=files, timeout=timeout_settings)

            if response.status_code != 200:
                print(
                    f"Error uploading to {context}. Status Code: {response.status_code}. Response content: {response.content}")
                try:
                    error_detail = response.json()
                except ValueError:
                    raise HTTPException(status_code=response.status_code, detail=f"Error: {response.text}")

                raise HTTPException(status_code=response.status_code, detail=error_detail)

            # Collect response data for successful uploads
            try:
                upload_response = response.json()
                responses.append(upload_response)
            except ValueError:
                raise HTTPException(status_code=500, detail="Received invalid JSON response from the server")

            # Configure the loader for the uploaded file
            loader_config_id = f"{context}_{file.filename.replace(' ', '_')}_loader"
            doc_store_collection_name = f"{context}_{file.filename.replace(' ', '_')}_collection"

            loader_config_data = {
                "config_id": loader_config_id,
                "path": f"data_stores/data/{context}",
                "loader_map": {
                  f"{file.filename.replace(' ', '_')}": "PyMuPDFLoader"
                },
                "loader_kwargs_map": {
                  f"{file.filename.replace(' ', '_')}": {"extract_images": True}
                },
                "metadata_map": {
                  f"{file.filename.replace(' ', '_')}": {
                    "source_context": f"{context}"
                  }
                },
                "default_metadata": {
                   "source_context": f"{context}"
                },
                "recursive": True,
                "max_depth": 5,
                "silent_errors": True,
                "load_hidden": True,
                "show_progress": True,
                "use_multithreading": True,
                "max_concurrency": 8,
                "exclude": [
                  "*.tmp",
                  "*.log"
                ],
                "sample_size": 10,
                "randomize_sample": True,
                "sample_seed": 42,
                "output_store_map": {
                  f"{file.filename.replace(' ', '_')}": {
                    "collection_name": doc_store_collection_name
                  }
                },
                "default_output_store": {
                  "collection_name": doc_store_collection_name
                }
              }

            # Configure the loader on the original API
            loader_response = await client.post(f"{NLP_CORE_SERVICE}/document_loaders/configure_loader", json=loader_config_data)
            if loader_response.status_code != 200 and loader_response.status_code != 400:
                raise HTTPException(status_code=loader_response.status_code, detail=loader_response.json())

            # Apply the loader to process the document
            load_response = await client.post(f"{NLP_CORE_SERVICE}/document_loaders/load_documents/{loader_config_id}", timeout=timeout_settings)
            if load_response.status_code != 200:
                raise HTTPException(status_code=load_response.status_code, detail=load_response.json())

            # Collect document processing results
            #processed_docs = load_response.json()

            ### Configure the Vector Store ###

            vector_store_config_id = f"{context}_vector_store_config"
            vector_store_id = f"{context}_vector_store"

            vector_store_config = {
                "config_id": vector_store_config_id,
                "store_id": vector_store_id,
                "vector_store_class": "Chroma",  # Example: using Chroma vector store, modify as necessary
                "params": {
                    "persist_directory": f"vector_stores/{context}"
                },
                "embeddings_model_class": "OpenAIEmbeddings",
                "embeddings_params": {
                    "api_key": get_random_openai_api_key()  # Seleziona una chiave API casuale
                },
                "description": f"Vector store for context {context}",
                "custom_metadata": {
                    "source_context": context
                }
            }

            # Configure the vector store
            vector_store_response = await client.post(
                f"{NLP_CORE_SERVICE}/vector_stores/vector_store/configure", json=vector_store_config, timeout=timeout_settings)
            if vector_store_response.status_code != 200 and vector_store_response.status_code != 400:
                raise HTTPException(status_code=vector_store_response.status_code, detail=vector_store_response.json())

            #vector_store_config_id = vector_store_response.json()["config_id"]

            ### Load the Vector Store ###
            load_vector_response = await client.post(f"{NLP_CORE_SERVICE}/vector_stores/vector_store/load/{vector_store_config_id}", timeout=timeout_settings)
            if load_vector_response.status_code != 200 and load_vector_response.status_code != 400:
                raise HTTPException(status_code=load_vector_response.status_code, detail=load_vector_response.json())

            ### Add Documents from the Document Store to the Vector Store ###
            # Use the document collection name associated with the context
            add_docs_response = await client.post(
                f"{NLP_CORE_SERVICE}/vector_stores/vector_store/add_documents_from_store/{vector_store_id}",
                params={"document_collection": doc_store_collection_name}, timeout=timeout_settings)
            if add_docs_response.status_code != 200:
                print(add_docs_response)
                raise HTTPException(status_code=add_docs_response.status_code, detail=add_docs_response.json())

        # Return the collected responses with file UUID and associated contexts
        return {"file_id": file_uuid, "contexts": contexts}

########################################################################################################################
########################################################################################################################


# Create a new context (directory)
@app.post("/contexts", response_model=ContextMetadata)
async def create_context(context_name: str = Form(...), description: Optional[str] = Form(None)):
    metadata = {"description": description} if description else None
    result = await create_context_on_server(context_name, metadata)
    return result

# Delete an existing context (directory)
@app.delete("/contexts/{context_name}", response_model=Dict[str, Any])
async def delete_context(context_name: str):
    result = await delete_context_on_server(context_name)
    # TODO: delete related vector store (and all related collection in document store)
    return result

# List all available contexts
@app.get("/contexts", response_model=List[ContextMetadata])
async def list_contexts():
    result = await list_contexts_from_server()
    return result

# Upload a file to multiple contexts
@app.post("/upload", response_model=FileUploadResponse)
async def upload_file_to_multiple_contexts(
        file: UploadFile = File(...),
        contexts: List[str] = Form(...),
        description: Optional[str] = Form(None)
):
    file_metadata = {"description": description} if description else None
    result = await upload_file_to_contexts(file, contexts, file_metadata)
    return result


# Helper function to list files by context
async def list_files_in_context(contexts: Optional[List[str]] = None):
    async with httpx.AsyncClient() as client:
        if contexts:
            # If contexts are provided, filter files by those contexts
            files = []
            for context in contexts:
                response = await client.get(f"{NLP_CORE_SERVICE}/data_stores/files", params={"subdir": context})
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail=response.json())
                files.extend(response.json())
            return files
        else:
            # No context specified, list all files across all contexts
            response = await client.get(f"{NLP_CORE_SERVICE}/data_stores/files")
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.json())
            return response.json()


# Helper function to delete files by UUID
async def delete_file_by_id(file_id: str):
    async with httpx.AsyncClient() as client:
        # List all contexts to find where the file exists
        response = await client.get(f"{NLP_CORE_SERVICE}/data_stores/files")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())

        # Delete the file from all contexts where the UUID matches
        files = response.json()
        for file in files:
            if file['custom_metadata'].get('file_uuid') == file_id:
                path = file['path']
                delete_response = await client.delete(f"{NLP_CORE_SERVICE}/data_stores/delete/{path}")
                if delete_response.status_code != 200:
                    raise HTTPException(status_code=delete_response.status_code, detail=delete_response.json())
        return {"detail": f"File with ID {file_id} deleted from all contexts"}


# Helper function to delete file by path
async def delete_file_by_path(file_path: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{NLP_CORE_SERVICE}/delete/data_stores/{file_path}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return {"detail": f"File at path {file_path} deleted successfully"}


# Endpoint to list files by specific context(s)
@app.get("/files", response_model=List[Dict[str, Any]])
async def list_files(contexts: Optional[List[str]] = Query(None)):
    """
    List files for specific contexts. If no contexts are provided, list all files.
    """
    result = await list_files_in_context(contexts)
    return result


# Endpoint to delete files by either UUID (deletes from all contexts) or path (deletes from a specific context)
@app.delete("/files")
async def delete_file(file_id: Optional[str] = Query(None), file_path: Optional[str] = Query(None)):
    """
    Delete a file by either its UUID (from all contexts) or its path (from a specific context).
    """
    if file_id:
        # Delete by UUID from all contexts
        result = await delete_file_by_id(file_id)
    elif file_path:
        # Delete by path from a specific context
        result = await delete_file_by_path(file_path)
    else:
        raise HTTPException(status_code=400, detail="Either file_id or file_path must be provided")

    return result
########################################################################################################################

@app.post("/upload_document")
async def upload_document(
        session_id: str = Form(...),
        file_id: str = Form(...),
        uploaded_file: UploadFile = File(...),
        description: Optional[str] = Form("")):

    _id = f"{session_id}-{file_id}"

    create_context_response = await create_context(context_name=_id, description=description)
    upload_file_response = await upload_file_to_contexts(file=uploaded_file, contexts=[_id], file_metadata=None)

    print(create_context_response)
    print(upload_file_response)

    configure_and_load_chain_response = await configure_and_load_chain_1(context=_id, model_name="gpt-4o-mini")

    print(configure_and_load_chain_response)

    chain_id = f"{_id}-doc_analysis_chain"

    query = {
        "chat_history": [],
        "input": "Analizza il documento fornito e crea una descrizione dettagliata del suo contenuto. usa lo strumento di ricerca in vector store molteplici volte, fornendo query da molteplici punti di vista. crea una mappa che permetta successivamente di orientarsi tra i contenuti del documento"
    }

    inference_kwargs = {}

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(f"{NLP_CORE_SERVICE}/chains/execute_chain/",
                                     json={"chain_id": chain_id, "query": query, "inference_kwargs": inference_kwargs})

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())

    print(response.json())

    data = {
        "session_id": session_id,
        "file_id": file_id,
        "file_description": response.json()["output"]
    }

    # scrivi in apposita collection relativa a session_id i risultati del processamento e dell upload dei file

    # {"session_id": "...", "file_id": "...", "description": "..."}

    db_name = f"{session_id}_db"
    host = "localhost"
    port = 27017

    # Creazione del database tramite l'API
    db_credentials = {
        "db_name": db_name,
        "host": host,
        "port": port
    }
    response = requests.post(f"{MONGO_SERVICE_URL}/create_database/", json=db_credentials)
    print(response.json())
    if response.status_code != 200 and response.status_code != 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Errore durante la creazione del database")


    response = requests.post(f"{MONGO_SERVICE_URL}/{db_name}/create_collection/",
                             params={"collection_name": "file_descriptions"})
    print(response.json())
    if response.status_code != 200 and response.status_code != 400:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Errore nella creazione della collezione.")

    response = requests.post(
        f"{MONGO_SERVICE_URL}/{db_name}/file_descriptions/add_item/",
        json=data
    )
    print(response.json())
    if response.status_code != 200 and response.status_code != 400:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Errore nell'aggiunta del documento.")

    return data

########################################################################################################################
#@app.post("/configure_and_load_chain_1/")
async def configure_and_load_chain_1(
    context: str = Query("default", title="Context", description="The context for the chain configuration"),
    model_name: str = Query("gpt-4o", title="Model Name", description="The name of the LLM model to load, default is gpt-4o")
):
    """
    Configura e carica una chain in memoria basata sul contesto dato.
    """

    timeout_settings = httpx.Timeout(600.0, connect=600.0, read=600.0, write=600.0)

    vector_store_config_id = f"{context}_vector_store_config"
    vector_store_id = f"{context}_vector_store"

    # Impostazione di configurazione per l'LLM basata su model_name (di default "gpt-4o")
    llm_config_id = f"chat-openai_{model_name}_config"
    llm_id = f"chat-openai_{model_name}"

    async with httpx.AsyncClient() as client:
        # 1. Caricamento dell'LLM
        load_llm_url = f"{NLP_CORE_SERVICE}/llms/load_model/{llm_config_id}"
        llm_response = await client.post(load_llm_url, timeout=timeout_settings)

        if llm_response.status_code != 200 and llm_response.status_code != 400:
            raise HTTPException(status_code=llm_response.status_code, detail=f"Errore caricamento LLM: {llm_response.text}")

        llm_load_result = llm_response.json()

        # 2. Configurazione del vector store
        vector_store_config = {
            "config_id": vector_store_config_id,
            "store_id": vector_store_id,
            "vector_store_class": "Chroma",  # Example: using Chroma vector store, modify as necessary
            "params": {
                "persist_directory": f"vector_stores/{context}"
            },
            "embeddings_model_class": "OpenAIEmbeddings",
            "embeddings_params": {
                "api_key": get_random_openai_api_key()  # Seleziona una chiave API casuale
            },
            "description": f"Vector store for context {context}",
            "custom_metadata": {
                "source_context": context
            }
        }

        # Configura il vector store
        vector_store_response = await client.post(
            f"{NLP_CORE_SERVICE}/vector_stores/vector_store/configure", json=vector_store_config, timeout=timeout_settings
        )
        if vector_store_response.status_code != 200 and vector_store_response.status_code != 400:
            raise HTTPException(status_code=vector_store_response.status_code, detail=vector_store_response.json())

        # Carica il vector store
        load_vector_response = await client.post(
            f"{NLP_CORE_SERVICE}/vector_stores/vector_store/load/{vector_store_config_id}", timeout=timeout_settings
        )
        if load_vector_response.status_code != 200 and load_vector_response.status_code != 400:
            raise HTTPException(status_code=load_vector_response.status_code, detail=load_vector_response.json())

    # Configurazione della chain
    chain_config = {
        "chain_type": "agent_with_tools",
        "config_id": f"{context}-doc_analysis_chain_config",
        "chain_id": f"{context}-doc_analysis_chain",
        "system_message": "you are an helpful assistant",
        "llm_id": llm_id,  # Usa l'ID del modello LLM configurato
        "tools": [{"name": "VectorStoreTools", "kwargs": {"store_id": f"{context}_vector_store"}}]
    }

    async with httpx.AsyncClient() as client:
        try:
            # 1. Configura la chain
            configure_url = f"{NLP_CORE_SERVICE}/chains/configure_chain/"
            configure_response = await client.post(configure_url, json=chain_config)

            if configure_response.status_code != 200 and configure_response.status_code != 400:
                raise HTTPException(status_code=configure_response.status_code, detail=f"Errore configurazione: {configure_response.text}")

            configure_result = configure_response.json()

            # 2. Carica la chain
            load_url = f"{NLP_CORE_SERVICE}/chains/load_chain/{chain_config['config_id']}"
            load_response = await client.post(load_url)

            if load_response.status_code != 200 and load_response.status_code != 400:
                raise HTTPException(status_code=load_response.status_code, detail=f"Errore caricamento: {load_response.text}")

            load_result = load_response.json()

            return {
                "message": "Chain configurata e caricata con successo.",
                "llm_load_result": llm_load_result,
                "config_result": configure_result,
                "load_result": load_result
            }

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Errore HTTP: {e.response.text}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

########################################################################################################################

@app.post("/configure_and_load_chain/")
async def configure_and_load_chain_2(
    session_id: str = Query("default", title="Session ID", description="The session id used for the chain configuration"),
    model_name: str = Query("gpt-4o", title="Model Name", description="The name of the LLM model to load, default is gpt-4o")
):
    """
    Configura e carica una chain in memoria.
    """

    timeout_settings = httpx.Timeout(600.0, connect=600.0, read=600.0, write=600.0)

    # usa session id per caricare mongo db e collection opportune,dunque estrai tutti i doc delle descrizioni e dei file id, dunque risali ai vector store e configura tutti i tools necessari all agente
    db_name = f"{session_id}_db"
    collection_name = "file_descriptions"
    query = {}

    response = requests.post(f"{MONGO_SERVICE_URL}/{db_name}/get_items/{collection_name}/", json=query)
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Errore nel recupero dei documenti.")

    print(response.json())

    file_descriptions = response.json()

    file_ids = [file_description["file_id"] for file_description in file_descriptions]
    vectorstore_ids = [f"{session_id}-{file_id}_vector_store" for file_id in file_ids]

    tools = [{"name": "VectorStoreTools", "kwargs": {"store_id": vectorstore_id}} for vectorstore_id in vectorstore_ids]
    tools.append({"name": "MongoDBTools",
                  "kwargs": {
                      "connection_string": "mongodb://localhost:27017",
                      "default_database": f"{session_id}_db",
                      "default_collection": "file_descriptions"
                  }})

    #vector_store_config_id = f"{context}_vector_store_config"
    #vector_store_id = f"{context}_vector_store"

    # Impostazione di configurazione per l'LLM basata su model_name (di default "gpt-4o")
    llm_config_id = f"chat-openai_{model_name}_config"
    llm_id = f"chat-openai_{model_name}"

    async with httpx.AsyncClient() as client:
        # 1. Caricamento dell'LLM
        load_llm_url = f"{NLP_CORE_SERVICE}/llms/load_model/{llm_config_id}"
        llm_response = await client.post(load_llm_url, timeout=timeout_settings)

        if llm_response.status_code != 200 and llm_response.status_code != 400:
            raise HTTPException(status_code=llm_response.status_code, detail=f"Errore caricamento LLM: {llm_response.text}")

        llm_load_result = llm_response.json()

    # Configurazione della chain
    chain_config = {
        "chain_type": "agent_with_tools",
        "config_id": f"{session_id}-workflow_generation_chain_config",
        "chain_id": f"{session_id}-workflow_generation_chain",
        "system_message": get_system_message(session_id, vectorstore_ids, file_descriptions),
        "llm_id": llm_id,  # Usa l'ID del modello LLM configurato
        "tools": tools
    }

    async with httpx.AsyncClient() as client:
        try:
            # 1. Configura la chain
            configure_url = f"{NLP_CORE_SERVICE}/chains/configure_chain/"
            configure_response = await client.post(configure_url, json=chain_config)

            if configure_response.status_code != 200 and configure_response.status_code != 400:
                raise HTTPException(status_code=configure_response.status_code, detail=f"Errore configurazione: {configure_response.text}")

            configure_result = configure_response.json()

            # 2. Carica la chain
            load_url = f"{NLP_CORE_SERVICE}/chains/load_chain/{chain_config['config_id']}"
            load_response = await client.post(load_url)

            if load_response.status_code != 200 and load_response.status_code != 400:
                raise HTTPException(status_code=load_response.status_code, detail=f"Errore caricamento: {load_response.text}")

            load_result = load_response.json()

            return {
                "message": "Chain configurata e caricata con successo.",
                "llm_load_result": llm_load_result,
                "config_result": configure_result,
                "load_result": load_result
            }

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Errore HTTP: {e.response.text}")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

########################################################################################################################

# Retrieve info associated with a single context (by ID or name)
@app.get("/context_info/{context_name}", response_model=Dict[str, Any])
async def get_context_info(context_name: str):
    result = await create_context_on_server(context_name)
    return result


# Helper function to query MongoDB
def query_mongo(collection_url: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
    response = requests.post(collection_url, json=query)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"MongoDB query failed: {response.text}")
    return response.json()


# Endpoint to get all workflows in a collection
@app.get("/get_all_workflows")
async def get_all_workflows(collection_name: str = Query(..., description="The name of the collection to query")):
    """
    Retrieve all workflows from a specific MongoDB collection.
    """
    collection_url = f"{MONGO_SERVICE_URL}/{collection_name}/get_items"
    query = {}  # Retrieve all items
    try:
        workflows = query_mongo(collection_url, query)
        return {"workflows": workflows}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Endpoint to get the last workflow in a collection
@app.get("/get_last_workflow")
async def get_last_workflow(session_id: str = Query(..., description="The session ID to query")):
    """
    Retrieve the last workflow for a specific session ID.
    """
    db_name = f"{session_id}_db"
    collection_name = "workflows"
    query = {}

    response = requests.post(f"{MONGO_SERVICE_URL}/{db_name}/get_items/{collection_name}/", json=query)
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Errore nel recupero dei documenti.")

    print(response.json())
    return response.json()


def execute_agent(chain_id: str, input_query: str, chat_history: List[Dict[str, str]] = []):
    api_url = "http://34.79.136.231:8100/chains/stream_events_chain"

    # Definire il payload della richiesta
    payload = {
        "chain_id": chain_id,
        "query": {
            "input": input_query,
            "chat_history": chat_history
        },
        "inference_kwargs": {}
    }

    # Eseguire la richiesta POST all'API
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Solleva un'eccezione per codici di errore HTTP
        #data = response.json()  # Decodifica la risposta JSON
        data = response.__dict__['_content'].decode()
        print("Risultato dell'API:")
        print(data)
        return data
        #print(json.dumps(data, indent=2))  # Stampa il risultato formattato
    except requests.exceptions.RequestException as e:
        print(f"Errore nella chiamata all'API: {e}")


'''@app.post("/generate_workflows", response_model=List[Dict[str, Any]])
async def generate_workflows(input_data: GenerateWorkflowsInput):
    """
    Genera workflow basati sui file forniti e un prompt specificato.
    Esegue l'upload dei file a contesti multipli utilizzando un ID univoco.
    """
    files = input_data.files
    prompt = input_data.prompt
    session_id = str(uuid.uuid4())[:10]  # Genera un ID univoco per la sessione
    results = []

    for file in files:
        try:
            # Decodifica il contenuto Base64
            decoded_content = base64.b64decode(file.content_base64)
            print(decoded_content)
            # Creazione dell'oggetto file per il caricamento
            upload_file = StarletteUploadFile(
                filename=f"{file.id_file}.txt",  # Aggiungi estensione se necessaria
                file=BytesIO(decoded_content),
                #content_type="application/octet-stream"
            )
            print(upload_file)
            # Esegui l'upload utilizzando la funzione
            response = await upload_document(
                session_id=session_id,
                file_id=file.id_file,
                uploaded_file=upload_file,
                description=file.description
            )
            print(response)

            input("...")
            # Aggiungi il risultato all'elenco dei risultati
            results.append({
                "file_id": file.id_file,
                "upload_response": response,
                "status": "success"
            })

        except Exception as e:
             print(f"[ERROR]: {e}")

    workflow_data = []
    configure_chain_url = f"http://127.0.0.1:8091/configure_and_load_chain/?session_id={session_id}"
    try:
        response = requests.post(configure_chain_url)
        if response.status_code == 200:
            print("Configure agent response:", response.json())
        else:
            print(f"Failed to configure agent: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"An error occurred during agent configuration: {e}")

    ####################################################################################################################
    # TODO:
    #  - tieni conto del prompt inviato in input (direttive e linee guida fornite dall'utente)
    #
    #input_instructions = [
    #    "ciao",
    #    "crea una workinstructions a caso e salvala, vai di fantasia senza le mie direttive. procedi con il salvataggio senza chiedermi il permesso",
    #    "salva la workinstructions generata nel db senza chiedermi conferma! procedi direttamente !!!"
    #]
    #chat_history = []
    #for message in input_instructions:

    #    # Use auto_generated=True to avoid duplicating messages in chat history
    #    agent_response = execute_agent(chain_id=f"{session_id}-workflow_generation_chain", input_query=message, chat_history=chat_history)
    #    chat_history.append({"role": "user", "content": message})
    #    chat_history.append({"role": "ai", "content": agent_response})
    ####################################################################################################################

    chat_history = []
    max_iterations = 5
    grado_di_scomposizione = "Alto"

    message_0 = f"osserva e analizza il docuemnto fornito, dunque ipotizza tutte le workflow che si possono creare (senza crearle) e associa ad esse i contenuti a cui fare riferimento (citando pagine di docuemnti e immagini contenute in essi) per crearle successivamente in dettaglio (le creerai nei prossimi messaggi). queste direttive sintentiche verranno usate dopo per sviluppare sequenzialmente i workflow dettalgiati. concentrati solo sulle workflow di configurazione per un massimo di {max_iterations}, inoltre assicurti di scrivere le proposte di workflow in lista numerata."

    agent_response = execute_agent(chain_id=f"{session_id}-workflow_generation_chain", input_query=message_0,
                                   chat_history=chat_history)

    chat_history.append({"role": "user", "content": message_0})
    chat_history.append({"role": "assistant", "content": agent_response})

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
            agent_response = execute_agent(chain_id=f"{session_id}-workflow_generation_chain", input_query=message,
                                           chat_history=chat_history)

            chat_history.append({"role": "user", "content": message_0})
            chat_history.append({"role": "assistant", "content": agent_response})
            if "<command=TERMINATION| TRUE |command=TERMINATION>" in agent_response:
                is_terminated = True
                break
    ####################################################################################################################

    try:
        get_last_workflow_url = f"http://127.0.0.1:8091/get_last_workflow?session_id={session_id}"
        response = requests.get(get_last_workflow_url)
        if response.status_code == 200:
            workflow_data = response.json()
        else:
            print(f"Failed to retrieve last workflow: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return workflow_data'''


@app.post("/generate_workflows", response_model=List[Dict[str, Any]])
async def generate_workflows(input_data: GenerateWorkflowsInput):
    """
    Genera workflow basati sui file forniti e un prompt specificato.
    Esegue l'upload dei file a contesti multipli utilizzando un ID univoco.
    """
    time.sleep(5)

    return {"output_id": str(uuid.uuid4())}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8091)




