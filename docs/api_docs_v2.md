# Documentazione Dettagliata dell'API Aggiornata

## Descrizione del Progetto

L'**API Aggiornata** è un sistema avanzato progettato per gestire contesti e file, integrando funzionalità di caricamento, gestione e analisi dei documenti. L'API si avvale di **FastAPI** per costruire un'interfaccia web robusta, interagendo con servizi esterni come un **NLP Core Service** e un servizio **MongoDB** per la gestione e l'archiviazione dei dati. L'API supporta operazioni CRUD (Create, Read, Update, Delete) su contesti e file, nonché la configurazione e il caricamento di catene di elaborazione basate su modelli di linguaggio di grandi dimensioni (LLM) per la generazione di workflow.

## Struttura del Progetto

- **app/**
  - **main.py**: Contiene l'applicazione FastAPI, gli endpoint e la logica di gestione delle richieste.
  - **models.py**: Definisce i modelli Pydantic per validare e serializzare i dati di input e output.
  - **utilities.py**: Contiene funzioni di utilità, tra cui `get_system_message`, utilizzata per generare il prompt dell’agente.
  - **config.json**: File di configurazione che contiene le impostazioni necessarie per l'API.
- **requirements.txt**: Elenco delle dipendenze del progetto.
- **README.md**: Documentazione generale del progetto.

## Prerequisiti

- **Python 3.7+**
- **Virtualenv** (opzionale ma consigliato)
- **MongoDB** in esecuzione e accessibile tramite l'URL configurato.
- **NLP Core Service** operativo e accessibile tramite l'URL configurato.
- **Chiavi API OpenAI** valide per l'utilizzo con i modelli di linguaggio.

## Installazione

1. **Clona il repository**

   ```bash
   git clone https://github.com/tuo-utente/updated-api.git
   cd updated-api
   ```

2. **Crea un ambiente virtuale** (opzionale ma consigliato)

   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Windows: venv\Scripts\activate
   ```

3. **Installa le dipendenze**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configura l'applicazione**

   Assicurati di configurare correttamente il file `config.json` con i seguenti parametri:

   ```json
   {
       "nlp_core_service": "http://localhost:8001",
       "mongodb_service": "http://localhost:27017",
       "openai_api_keys": ["your_openai_api_key1", "your_openai_api_key2"]
   }
   ```

## Avvio dell'Applicazione

Puoi avviare l'applicazione utilizzando Uvicorn:

```bash
uvicorn app.main:app --reload
```

- **`app.main:app`**: Indica il percorso dell'applicazione FastAPI.
- **`--reload`**: Riavvia automaticamente il server quando rileva modifiche al codice (utile in fase di sviluppo).

L'API sarà disponibile all'indirizzo `http://localhost:8000`.

## Middleware

L'API utilizza il middleware CORS per permettere le richieste da tutte le origini:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permetti tutte le origini
    allow_credentials=True,
    allow_methods=["*"],  # Permetti tutti i metodi (GET, POST, OPTIONS, ecc.)
    allow_headers=["*"],  # Permetti tutti gli headers
)
```

## Modelli di Dati

### `ContextMetadata`

Rappresenta i metadati associati a un contesto.

```python
class ContextMetadata(BaseModel):
    path: str
    custom_metadata: Optional[Dict[str, Any]] = None
```

- **`path`**: Percorso del contesto.
- **`custom_metadata`**: Metadati personalizzati opzionali.

### `FileUploadResponse`

Rappresenta la risposta dopo il caricamento di un file.

```python
class FileUploadResponse(BaseModel):
    file_id: str
    contexts: List[str]
```

- **`file_id`**: Identificatore univoco del file.
- **`contexts`**: Lista di contesti a cui il file è stato caricato.

## Endpoint dell'API

### Creazione di un Nuovo Contesto

- **Metodo**: `POST`
- **Endpoint**: `/contexts`
- **Descrizione**: Crea un nuovo contesto (directory) con un nome e una descrizione opzionale.

#### Richiesta

- **Parametri del Form**:
  - `context_name` (string, richiesto): Nome del contesto.
  - `description` (string, opzionale): Descrizione del contesto.

#### Risposta

- **Codice 200**: Contesto creato con successo.
- **Corpo della Risposta**:

  ```json
  {
      "path": "nome_del_contesto",
      "custom_metadata": {
          "description": "Descrizione del contesto"
      }
  }
  ```

#### Esempio di Richiesta con cURL

```bash
curl -X POST "http://localhost:8000/contexts" \
  -F "context_name=nuovo_contesto" \
  -F "description=Descrizione del nuovo contesto"
```

### Eliminazione di un Contesto Esistente

- **Metodo**: `DELETE`
- **Endpoint**: `/contexts/{context_name}`
- **Descrizione**: Elimina un contesto esistente specificato per nome.

#### Parametri

- **Path Parameter**:
  - `context_name` (string, richiesto): Nome del contesto da eliminare.

#### Risposta

- **Codice 200**: Contesto eliminato con successo.
- **Corpo della Risposta**:

  ```json
  {
      "detail": "Contesto eliminato con successo."
  }
  ```

#### Esempio di Richiesta con cURL

```bash
curl -X DELETE "http://localhost:8000/contexts/nuovo_contesto"
```

### Caricamento di un File in Più Contesti

- **Metodo**: `POST`
- **Endpoint**: `/upload`
- **Descrizione**: Carica un file in uno o più contesti specificati, configurando anche il vector store e la catena di elaborazione.

#### Richiesta

- **Parametri del Form**:
  - `file` (UploadFile, richiesto): File da caricare.
  - `contexts` (List[str], richiesto): Lista di contesti separati da virgola.
  - `description` (string, opzionale): Descrizione del file.

#### Risposta

- **Codice 200**: File caricato con successo.
- **Corpo della Risposta**:

  ```json
  {
      "file_id": "uuid_generato",
      "contexts": ["contesto1", "contesto2"]
  }
  ```

#### Esempio di Richiesta con cURL

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@path/al/file" \
  -F "contexts=contesto1,contesto2" \
  -F "description=Descrizione del file"
```

### Caricamento di un Documento e Configurazione del Workflow

- **Metodo**: `POST`
- **Endpoint**: `/upload_document`
- **Descrizione**: Carica un documento associato a una sessione e configura una chain di elaborazione per analizzare il contenuto del documento e generare un workflow.

#### Prompt dell'Agente per il Workflow

L'agente utilizza un prompt per ottenere direttive dettagliate e creare workflow secondo un formato specifico, basandosi sui file caricati e i dati MongoDB. **Prompt**:

```python
def get_system_message(session_id, vectorstore_ids, file_descriptions):
    vectorstore_ids_str = ", ".join(vectorstore_ids)
    system_message = f"""Sei un assistente intelligente con le seguenti capacità:
    
    [CONTENUTO DEL PROMPT DELL'AGENTE COME DESCRITTO SOPRA]
    """
    return system_message
```

#### Esempio di Workflow

L’agente costruirà workflow in JSON seguendo uno schema prestabilito per ogni task con campi specifici, utilizzando i vector store per recuperare contenuti dettagliati e MongoDB per gestire il database.

#### Risposta

- **Codice 200**: Documento caricato, workflow generato e salvato con successo.
- **Corpo della Risposta**:

  ```json
  {
      "session_id": "sessione_123",
      "file_id": "file_456",
      "file_description": "Descrizione dettagliata del contenuto del documento."
  }
  ```

#### Esempio di Richiesta con cURL

```bash
curl -X POST "http://localhost:8000/upload_document" \
  -F "session_id=sessione_123" \
  -F "file_id=file_456" \
  -F "uploaded_file=@path

/al/documento" \
  -F "description=Descrizione del documento"
```

---

### Configurazione e Caricamento di una Chain

- **Metodo**: `POST`
- **Endpoint**: `/configure_and_load_chain`
- **Descrizione**: Configura e carica una catena di elaborazione utilizzando MongoDB e vector stores.

---

### Gestione degli Errori

L'API utilizza `HTTPException` per gestire gli errori e restituire risposte appropriate con codici di stato HTTP. 

