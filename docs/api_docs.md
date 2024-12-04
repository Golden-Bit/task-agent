# API per la Gestione di Workflow e Documenti

---

## Endpoint `/generate_workflows`

## Descrizione

L'endpoint `/generate_workflows` consente di generare workflow basati su una serie di file forniti dall'utente e un prompt specificato. I file vengono caricati e associati a una sessione univoca. L'endpoint processa i documenti caricati e utilizza modelli di linguaggio per creare workflow pertinenti.

## Dettagli della Richiesta

- **URL**: `/generate_workflows`
- **Metodo HTTP**: `POST`
- **Tipo di Contenuto**: `application/json`

### Corpo della Richiesta (`GenerateWorkflowsInput`)

La richiesta deve includere un JSON con la seguente struttura:

```json
{
  "files": [
    {
      "id_file": "string",
      "content_base64": "string",
      "description": "string (opzionale)"
    },
    ...
  ],
  "prompt": "string"
}
```

- **files**: Lista di file da processare.
  - **id_file**: Identificatore univoco del file.
  - **content_base64**: Contenuto del file codificato in Base64.
  - **description**: Descrizione opzionale del file.
- **prompt**: Prompt fornito dall'utente per guidare la generazione dei workflow.

## Dettagli della Risposta

La risposta sarà una lista di oggetti JSON contenenti informazioni sui workflow generati:

- **file_id**: Identificatore del file processato.
- **upload_response**: Risposta relativa all'upload e al processamento del file.
- **status**: Stato dell'operazione (es. "success").

### Esempio di Risposta

```json
[
  {
    "file_id": "documento1",
    "upload_response": {
      "session_id": "abc123",
      "file_id": "documento1",
      "file_description": "Descrizione dettagliata del contenuto del file."
    },
    "status": "success"
  },
  ...
]
```

## Flusso Operativo

1. **Decodifica e Caricamento dei File**: I file forniti vengono decodificati dal formato Base64 e caricati utilizzando l'endpoint interno `/upload_document`.

2. **Processamento dei Documenti**: Ogni documento viene associato a una sessione e un file ID univoci. Viene analizzato per estrarre una descrizione dettagliata del contenuto.

3. **Configurazione della Chain**: Viene configurata una chain specifica per la sessione corrente, utilizzando modelli di linguaggio (LLM) per l'elaborazione.

4. **Esecuzione dell'Agente**: Viene eseguito un agente che, basandosi sul prompt fornito e sui documenti caricati, genera i workflow richiesti.

5. **Recupero dei Workflow**: Al termine del processamento, vengono recuperati i workflow generati e restituiti nella risposta.

## Note Importanti

- **Codifica Base64**: Assicurarsi che il contenuto dei file sia correttamente codificato in Base64 prima dell'invio.

- **Gestione delle Eccezioni**: In caso di errore, l'endpoint restituirà messaggi di errore dettagliati con lo status code appropriato.

- **Session ID**: Ogni chiamata genera un nuovo `session_id` univoco, utilizzato per tracciare i file e i workflow associati.

## Esempio di Utilizzo

### Richiesta

```http
POST /generate_workflows HTTP/1.1
Host: api.example.com
Content-Type: application/json

{
  "files": [
    {
      "id_file": "file1",
      "content_base64": "VGhpcyBpcyBhIHRlc3QgZmlsZSBjb250ZW50Lg==",
      "description": "File di esempio"
    }
  ],
  "prompt": "Genera un workflow basato sul documento fornito."
}
```

### Risposta

```json
[
  {
    "file_id": "file1",
    "upload_response": {
      "session_id": "abcd1234",
      "file_id": "file1",
      "file_description": "Il documento contiene informazioni su..."
    },
    "status": "success"
  }
]
```

## Dipendenze Esterne

- **NLP Core Service**: Utilizzato per l'analisi dei documenti e l'esecuzione dell'agente.

- **MongoDB Service**: I dettagli dei workflow e delle sessioni vengono salvati su un database MongoDB dedicato.

## Considerazioni Finali

Questo endpoint facilita la generazione automatizzata di workflow basati su documenti forniti dall'utente e specifiche direttive. È essenziale assicurarsi che i file siano correttamente formattati e che il prompt sia chiaro per ottenere risultati ottimali.

---

**Fine della Documentazione**