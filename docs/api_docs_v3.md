# Documentazione Endpoint API

Questa sezione fornisce una descrizione dettagliata degli endpoint principali contenuti nel frammento di codice. Gli endpoint si concentrano sulla gestione dei documenti, sulla configurazione e sul caricamento di catene di elaborazione (workflow) utilizzando MongoDB e vector stores.

---

## 1. **Caricamento di un Documento e Generazione di Workflow**

### Endpoint: `/upload_document`

- **Metodo**: `POST`
- **Descrizione**: Questo endpoint carica un documento associato a una sessione, configura il contesto e genera una catena di elaborazione per analizzare il contenuto del documento e generare un workflow.

### Richiesta

#### Parametri
- **Form Parameters**:
  - `session_id` (string, richiesto): ID della sessione.
  - `file_id` (string, richiesto): Identificatore del file.
  - `uploaded_file` (UploadFile, richiesto): Documento da caricare.
  - `description` (string, opzionale): Descrizione del documento.

### Flusso Operativo
1. **Creazione di un Contesto**:
   - Genera un contesto univoco combinando `session_id` e `file_id`.
   - Crea il contesto con la descrizione fornita.

2. **Caricamento del File**:
   - Carica il documento nei contesti configurati.

3. **Configurazione della Catena di Analisi**:
   - Configura e carica una catena (`chain_id`) per analizzare il documento utilizzando vector stores.

4. **Esecuzione della Catena**:
   - Esegue la catena per analizzare il documento e ottenere una descrizione dettagliata.

5. **Salvataggio nel Database**:
   - Crea un database specifico per la sessione.
   - Salva i risultati dell’analisi (descrizione del file) nella collezione `file_descriptions`.

### Risposta

- **Codice 200**: Documento caricato, analizzato e salvato con successo.
- **Corpo della Risposta**:
  ```json
  {
      "session_id": "sessione_123",
      "file_id": "file_456",
      "file_description": "Descrizione dettagliata del contenuto del documento."
  }
  ```

### Esempio di Richiesta (cURL)
```bash
curl -X POST "http://localhost:8000/upload_document" \
  -F "session_id=sessione_123" \
  -F "file_id=file_456" \
  -F "uploaded_file=@path/al/documento" \
  -F "description=Descrizione del documento"
```

---

## 2. **Configurazione e Caricamento della Catena (Metodo 1)**

### Endpoint: `/configure_and_load_chain_1`

- **Metodo**: `POST` (attualmente commentato)
- **Descrizione**: Configura e carica una catena di analisi utilizzando un contesto specifico e un modello LLM.

### Richiesta

#### Parametri
- **Query Parameters**:
  - `context` (string, opzionale, default: `"default"`): Contesto per la configurazione della catena.
  - `model_name` (string, opzionale, default: `"gpt-4o-mini"`): Nome del modello LLM.

### Flusso Operativo
1. **Caricamento del Modello LLM**:
   - Configura e carica il modello LLM specificato.

2. **Configurazione del Vector Store**:
   - Configura il vector store associato al contesto, utilizzando `Chroma` come classe predefinita.

3. **Configurazione della Catena**:
   - Crea una catena di analisi utilizzando strumenti come `VectorStoreTools`.

4. **Caricamento della Catena**:
   - Carica la catena configurata nel servizio NLP.

### Risposta

- **Codice 200**: Catena configurata e caricata con successo.
- **Corpo della Risposta**:
  ```json
  {
      "message": "Chain configurata e caricata con successo.",
      "llm_load_result": { /* Dettagli del modello LLM */ },
      "config_result": { /* Dettagli della configurazione */ },
      "load_result": { /* Dettagli del caricamento */ }
  }
  ```

### Esempio di Richiesta (cURL)
```bash
curl -X POST "http://localhost:8000/configure_and_load_chain_1?context=my_context&model_name=gpt-4o-mini"
```

---

## 3. **Configurazione e Caricamento della Catena (Metodo 2)**

### Endpoint: `/configure_and_load_chain`

- **Metodo**: `POST`
- **Descrizione**: Configura e carica una catena di analisi basata su una sessione, recuperando le descrizioni dei file e configurando gli strumenti necessari.

### Richiesta

#### Parametri
- **Query Parameters**:
  - `session_id` (string, richiesto): ID della sessione.
  - `model_name` (string, opzionale, default: `"gpt-4o-mini"`): Nome del modello LLM.

### Flusso Operativo
1. **Recupero dei File**:
   - Accede alla collezione `file_descriptions` nel database specifico della sessione per ottenere descrizioni e ID dei file.

2. **Configurazione degli Strumenti**:
   - Configura strumenti come `VectorStoreTools` per ogni file.
   - Aggiunge strumenti per l’accesso a MongoDB.

3. **Caricamento del Modello LLM**:
   - Configura e carica il modello LLM specificato.

4. **Configurazione della Catena**:
   - Configura una catena utilizzando gli strumenti configurati e il prompt specifico per l'agente.

5. **Caricamento della Catena**:
   - Carica la catena configurata nel servizio NLP.

### Risposta

- **Codice 200**: Catena configurata e caricata con successo.
- **Corpo della Risposta**:
  ```json
  {
      "message": "Chain configurata e caricata con successo.",
      "llm_load_result": { /* Dettagli del modello LLM */ },
      "config_result": { /* Dettagli della configurazione */ },
      "load_result": { /* Dettagli del caricamento */ }
  }
  ```

### Esempio di Richiesta (cURL)
```bash
curl -X POST "http://localhost:8000/configure_and_load_chain?session_id=sessione_123&model_name=gpt-4o-mini"
```