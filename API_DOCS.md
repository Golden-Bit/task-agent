
# API DOCUMENTATION

---

## 1. Endpoint: `POST /upload_files_for_workflow`

**Funzionalità**  
Questo endpoint avvia, in **background**, il caricamento di una lista di file (in formato Base64) associati a una determinata sessione.

**Request Body**  
Il contenuto deve essere in formato JSON e corrispondere al modello `UploadWorkflowFilesInput`, così strutturato:

```json
{
  "session_id": "string",
  "files": [
    {
      "id_file": "string",
      "content_base64": "string (Base64)",
      "description": "string (opzionale)"
    }
  ]
}
```

- **session_id** *(string, obbligatorio)*: l’ID univoco della sessione.
- **files** *(array, obbligatorio)*: lista di oggetti che rappresentano i file da caricare.
  - **id_file** *(string)*: identificativo univoco del file.
  - **content_base64** *(string)*: contenuto del file in formato Base64.
  - **description** *(string, opzionale)*: descrizione breve del file.

**Comportamento**  
- Viene avviato un **task in background** che:
  1. Decodifica il Base64.
  2. Esegue l’upload fisico e la configurazione di elaborazione del documento (incluso il caricamento in un Vector Store).
  3. Invoca un’eventuale API esterna (metodo `upload_media_files`) per segnalare l’avvenuto caricamento.
  4. Scrive i risultati in un file JSON locale (per traccia e log).
- La **risposta** immediata (codice `202 Accepted`) indica solo che il processo è stato avviato con successo.

**Response**  
```json
{
  "detail": "Upload process started in background.",
  "output_file": "workflowgeneration_output/<NOME_FILE>.json"
}
```
- `detail`: messaggio di conferma.
- `output_file`: percorso (locale) dove verrà salvato il risultato completo dell’elaborazione.

---

## 2. Endpoint: `POST /generate_workflow`

**Funzionalità**  
Avvia, in **background**, la generazione di workflow a partire da un prompt e da eventuali file già caricati.

**Request Body**  
Deve rispettare il modello `GenerateWorkflowInput`:

```json
{
  "session_id": "string",
  "prompt": "string",
  "max_iterations": 5
}
```

- **session_id** *(string, obbligatorio)*: l’ID univoco della sessione (coincide con quanto usato in precedenza per caricare i file).
- **prompt** *(string, obbligatorio)*: istruzioni generali per la generazione dei workflow.
- **max_iterations** *(integer, default=5)*: numero massimo di workflow generabili.

**Comportamento**  
1. Esegue internamente la configurazione della chain (se necessario) tramite la funzione `configure_and_load_chain_2`.
2. Interagisce con un agente (che ha accesso ai file caricati nella sessione) per generare un set di workflow.  
3. Esegue più “turni” di conversazione con l’agente, fino al raggiungimento di `max_iterations` o di un segnale di terminazione.
4. Al termine, recupera i workflow dal DB (funzione `get_last_workflow` in background) e invia i dati a un’eventuale API esterna (`send_workflows`).
5. Scrive i risultati in un file JSON locale (nel path `workflowgeneration_output/`).

**Response**  
```json
{
  "detail": "Workflow generation started in background.",
  "output_file": "workflowgeneration_output/<NOME_FILE>.json"
}
```
- `detail`: messaggio di conferma.
- `output_file`: percorso (locale) dove verrà salvato il risultato finale.

---

## 3. Endpoint: `POST /chat_with_agent`

**Funzionalità**  
Consente di inviare un messaggio **sincrono** all’agente (LLM) associato alla sessione e ricevere immediatamente la risposta.

**Request Body**  
Il modello di riferimento è `ChatWithAgentInput`:

```json
{
  "session_id": "string",
  "user_input": "string",
  "chat_history": [
    {
      "role": "string",
      "content": "string"
    }
  ]
}
```

- **session_id** *(string, obbligatorio)*: l’ID univoco della sessione.
- **user_input** *(string, obbligatorio)*: testo del messaggio che si vuole inviare all’agente.
- **chat_history** *(array di oggetti, opzionale)*: storico della conversazione, in cui ogni elemento contiene:
  - **role**: "user" o "assistant"
  - **content**: il testo scambiato nel turno conversazionale precedente.

**Comportamento**  
1. (Opzionale) Tenta di riconfigurare la chain della sessione (tramite `configure_and_load_chain_2`) per assicurarsi che l’agente sia pronto.
2. Invia `user_input` all’agente (specificando eventuale `chat_history`).
3. Ritorna la risposta testuale dell’agente.

**Response**  
```json
{
  "assistant_response": "<RISPOSTA_GENERATA_DELL'AGENTE>"
}
```
- `assistant_response`: testo della risposta dell’agente (può contenere tokens, JSON, stringhe di sistema, ecc., a seconda della configurazione della chain).

---

## 4. Endpoint: `GET /get_last_workflow`

**Funzionalità**  
Recupera l’ultimo workflow associato a una determinata sessione dal database MongoDB.

**Query Parameter**  
- **session_id** *(string, obbligatorio)*: l’ID della sessione di cui si vogliono recuperare i workflow.

**Esempio di chiamata**  
```
GET /get_last_workflow?session_id=mysession123
```

**Comportamento**  
- Esegue una query su MongoDB (`collection_name = "workflows"`) nel database `session_id_db`.
- Ritorna l’insieme di workflow trovati (tecnicamente, l’ultimo o più di uno, in base alla struttura).

**Response**  
Esempio di risposta (array di documenti in JSON):
```json
[
  {
    "_id": "64f2ec5fa2d4f9b2b87d",
    "session_id": "mysession123",
    "workflow_id": "abcde-12345",
    "steps": [...],
    "created_at": "2025-01-28T10:15:00Z"
  },
  ...
]
```
> Il campo `_id` è tipico di MongoDB. Il contenuto effettivo può variare in base a come i workflow sono salvati.

---

