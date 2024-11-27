# Workflow Generator API

## Descrizione del Progetto

Il **Workflow Generator API** è un sistema progettato per generare automaticamente workflow complessi basati su input ricchi di contenuti, tra cui documenti, media e istruzioni fornite dall'utente. Utilizzando un agente LLM (Large Language Model), l'API analizza i dati di input per creare un workflow strutturato compatibile con Camunda, ottimizzando così il processo di costruzione e organizzazione dei workflow.

## Struttura del Progetto

- **app/**
  - **main.py**: Contiene l'applicazione FastAPI, gli endpoint e la logica di gestione delle richieste.
  - **models.py**: Contiene le definizioni dei modelli Pydantic per validare e serializzare i dati di input e output.
- **docs/**
  - **api_docs.md**: Documentazione dettagliata dell'API, inclusi endpoint, modelli di dati ed esempi.
  - **task_schema.md**: Descrizione dello schema dei task, con dettagli sui campi e sulle strutture dati utilizzate.
- **README.md**: Documentazione generale del progetto (questo file).

## Prerequisiti

- **Python 3.7+**
- **Virtualenv** (opzionale ma consigliato)

## Installazione

1. **Clona il repository**

   ```bash
   git clone https://github.com/tuo-utente/workflow-generator-api.git
   cd workflow-generator-api
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

## Configurazione

Attualmente, il progetto non richiede configurazioni aggiuntive. Tuttavia, se prevedi di connetterti a un agente LLM esterno, potresti dover configurare le credenziali o gli endpoint API nell'apposito modulo (ad esempio, `agent.py`).

## Avvio dell'Applicazione

Puoi avviare l'applicazione in due modi:

### 1. Utilizzando `main.py`

Esegui direttamente lo script `main.py`:

```bash
python app/main.py
```

**Nota**: Assicurati che la funzione `generate_workflow` sia correttamente implementata o utilizza il placeholder fornito.

### 2. Utilizzando Uvicorn

Esegui l'applicazione con Uvicorn per un ambiente di produzione leggero:

```bash
uvicorn app.main:app --reload
```

- `app.main:app` indica il percorso dell'applicazione FastAPI.
- `--reload` fa sì che Uvicorn riavvii il server ogni volta che rileva modifiche al codice (utile in fase di sviluppo).

## Utilizzo dell'API

Una volta avviata l'applicazione, l'API sarà disponibile all'indirizzo `http://localhost:8000`.

### Documentazione Interattiva

Puoi accedere alla documentazione interattiva dell'API tramite:

- **Swagger UI**: `http://localhost:8000/docs`
- **Redoc**: `http://localhost:8000/redoc`

Queste interfacce ti permettono di esplorare gli endpoint disponibili, vedere i modelli di dati e testare le richieste direttamente dal browser.

### Endpoint Principale

- **Generazione del Workflow**

  - **Metodo**: `POST`
  - **Endpoint**: `/generate-workflow`
  - **Descrizione**: Genera un workflow strutturato basato sul `README` e sui media forniti dall'utente.

Per dettagli su come utilizzare l'endpoint e sulla struttura dei dati di input/output, consulta la [documentazione dell'API](docs/api_docs.md).

## Documentazione

- **API Documentation**: [docs/api_docs.md](docs/api_docs.md)
  - Contiene una descrizione dettagliata dell'API, inclusi endpoint, modelli di dati, esempi di richieste e risposte, codici di stato HTTP e informazioni sul trattamento degli errori.
- **Task Schema**: [docs/task_schema.md](docs/task_schema.md)
  - Descrive in dettaglio lo schema dei task, inclusi i campi comuni e specifici per ogni tipo di task (`UserTask`, `ServiceTask`, `ExternalTask`), con tabelle esplicative e descrizioni dei campi.

## Struttura dei File

- **app/main.py**

  Contiene l'applicazione FastAPI e definisce gli endpoint dell'API. Include la logica per gestire le richieste e invocare l'agente LLM (da implementare).

- **app/models.py**

  Definisce i modelli Pydantic utilizzati per la validazione e la serializzazione dei dati di input e output. Include modelli per i media, i task e le strutture dati comuni.

## Testing

Per testare l'API, puoi utilizzare strumenti come:

- **cURL**: per inviare richieste HTTP dal terminale.
- **Postman**: per testare e monitorare le tue API.
- **Swagger UI**: direttamente dalla documentazione interattiva.

**Esempio di Richiesta con cURL**:

```bash
curl -X POST "http://localhost:8000/generate-workflow" \
  -H "Content-Type: application/json" \
  -d '{
        "readme": "Questo workflow guida l'\''utente attraverso il montaggio di un mobile...",
        "media": {
          "documents": [...],
          "images": [...],
          "videos": [...]
        }
      }'
```

## Dipendenze

Le dipendenze del progetto sono specificate nel file `requirements.txt`. Ecco alcune delle principali:

- **FastAPI**: Framework web moderno e ad alte prestazioni per costruire API con Python.
- **Uvicorn**: Server ASGI veloce per Python.
- **Pydantic**: Per la validazione dei dati e la gestione dei modelli.
- **Requests**: Per effettuare richieste HTTP (se necessario per connettersi all'agente LLM).
