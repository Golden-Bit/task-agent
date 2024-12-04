# Documentazione dell'Agente Intelligente

## Panoramica Generale

L'agente sviluppato è una soluzione avanzata progettata per creare workflow dettagliati basati su documenti caricati e direttive fornite dall'utente. L'agente utilizza strumenti di gestione dei dati come **MongoDB** e **Vector Stores** per l'elaborazione e l'analisi del contenuto, combinandoli con modelli di linguaggio di grandi dimensioni (LLM). Questo documento descrive in dettaglio la struttura, il funzionamento e l'utilizzo degli strumenti da parte dell'agente.

---

## Struttura dell'Agente

### Componenti Principali

1. **Integrazione con MongoDB**:
   - MongoDB è utilizzato per archiviare descrizioni dei file e workflow generati.
   - Ogni sessione ha un database dedicato con le seguenti collezioni:
     - **file_descriptions**: Contiene informazioni sui file caricati (ID, nome, descrizione).
     - **workflows**: Archivia i workflow generati.

2. **Vector Stores**:
   - Strumento per la rappresentazione e l'analisi dei contenuti tramite embeddings vettoriali.
   - Utilizza **Chroma** come backend per i vector stores.
   - Ogni file caricato è associato a un vector store per consentire ricerche contestuali avanzate.

3. **LLM**:
   - Modelli di linguaggio come `gpt-4o-mini` vengono utilizzati per analizzare il contenuto e generare workflow basati sulle direttive dell'utente.

---

## Flusso Operativo

### 1. **Creazione del Contesto**

Ogni documento caricato è associato a un contesto univoco identificato da una combinazione di `session_id` e `file_id`. Il contesto è registrato nel sistema tramite l'endpoint `/contexts`, includendo una descrizione opzionale.

- **Strumenti Utilizzati**:
  - **MongoDB**: Salva il contesto nel database.
  - **Vector Stores**: Configura un vector store associato al contesto.

---

### 2. **Caricamento dei File**

I file caricati sono processati e associati ai contesti tramite i seguenti passaggi:
1. **Upload del File**:
   - I file sono caricati nel sistema tramite l'endpoint `/upload`.
   - Metadati come il nome e la descrizione del file sono salvati.

2. **Configurazione dei Loader**:
   - Configura un loader (ad es. `PyMuPDFLoader`) per estrarre informazioni dal file.

3. **Configurazione del Vector Store**:
   - Configura un vector store per ogni contesto.
   - Esegue l'aggiunta del contenuto estratto al vector store.

---

### 3. **Generazione del Workflow**

1. **Recupero dei File**:
   - L'agente interroga la collezione `file_descriptions` in MongoDB per ottenere le descrizioni dei file caricati.

2. **Analisi dei Documenti**:
   - Utilizza il vector store per approfondire i contenuti rilevanti.

3. **Configurazione e Caricamento della Catena**:
   - Configura una chain specifica per il workflow.
   - Associa gli strumenti necessari:
     - **VectorStoreTools**: Per effettuare ricerche contestuali nei vector stores.
     - **MongoDBTools**: Per accedere e manipolare i dati in MongoDB.

4. **Creazione del Workflow**:
   - Genera un workflow dettagliato seguendo il formato JSON fornito.
   - Associa ogni task ai file rilevanti, specificando:
     - **ID del File**.
     - **Descrizione** e **Pagina** (ottenute dal vector store).

5. **Scrittura in MongoDB**:
   - Salva il workflow generato nella collezione `workflows`.

---

## Utilizzo degli Strumenti

### **1. MongoDB**

L'agente utilizza MongoDB principalmente per l'archiviazione e il recupero dei dati relativi a file e workflow.

- **Collezione `file_descriptions`**:
  - Contiene informazioni sui file caricati, inclusi:
    - `file_id`: Identificatore univoco del file.
    - `description`: Descrizione dettagliata.
  - Query tipica:
    ```json
    {}
    ```
    (Recupera tutti i documenti).

- **Collezione `workflows`**:
  - Salva il workflow generato in formato JSON.

---

### **2. Vector Stores**

I vector stores sono configurati per ogni contesto e vengono utilizzati per effettuare ricerche contestuali nei documenti caricati.

- **Configurazione**:
  - Ogni vector store è configurato con:
    - Classe: `Chroma`.
    - Modello di embeddings: `OpenAIEmbeddings`.

- **Esecuzione delle Ricerche**:
  - Effettua query multiple da diversi punti di vista per arricchire il workflow con informazioni dettagliate.

---

### **3. LLM**

L'agente utilizza modelli di linguaggio per analizzare le direttive dell'utente e generare task per il workflow.

---

## Esempio di Workflow Generato

```json
{
  "workflow": [
    {
      "id": "task1",
      "name": "Analisi preliminare",
      "description": "Esegui un'analisi preliminare del documento per estrarre informazioni chiave.",
      "type": "userTask",
      "assignee": "Analista",
      "candidateGroups": ["Tecnici"],
      "formKey": "preliminaryAnalysisForm",
      "mediaContent": {
        "documents": [
          {
            "id": "file1",
            "name": "Manuale Utente (pagina 3)",
            "description": "Sezione introduttiva al sistema."
          }
        ]
      },
      "conditions": [],
      "variables": {}
    },
    {
      "id": "task2",
      "name": "Configurazione dei parametri",
      "description": "Configura i parametri per l'analisi dettagliata.",
      "type": "userTask",
      "assignee": "Tecnico",
      "candidateGroups": ["Ingegneri"],
      "formKey": "parameterSetupForm",
      "mediaContent": {
        "documents": [
          {
            "id": "file2",
            "name": "Specifiche tecniche (pagina 12)",
            "description": "Dettagli sui parametri configurabili."
          }
        ]
      },
      "conditions": [
        {
          "conditionExpression": "task1.completed",
          "nextTaskId": "task3"
        }
      ],
      "variables": {}
    }
  ]
}
```
