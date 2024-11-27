# Documentazione Dettagliata dell'API

## Indice

1. [Introduzione](#introduzione)
2. [Panoramica dell'API](#panoramica-dellapi)
3. [Autenticazione](#autenticazione)
4. [Endpoint](#endpoint)
   - [1. Generazione del Workflow](#1-generazione-del-workflow)
5. [Modelli di Dati](#modelli-di-dati)
   - [1. Modello di Input: `WorkflowInput`](#1-modello-di-input-workflowinput)
   - [2. Modello di Output: `WorkflowOutput`](#2-modello-di-output-workflowoutput)
   - [3. Modelli dei Task](#3-modelli-dei-task)
6. [Esempi di Richieste e Risposte](#esempi-di-richieste-e-risposte)
   - [1. Esempio di Richiesta](#1-esempio-di-richiesta)
   - [2. Esempio di Risposta](#2-esempio-di-risposta)
7. [Codici di Stato HTTP](#codici-di-stato-http)
8. [Error Handling](#error-handling)
9. [Considerazioni Finali](#considerazioni-finali)

---

## Introduzione

Questa documentazione fornisce una descrizione dettagliata dell'API per la generazione automatizzata di workflow basati su input complessi, tra cui documenti, media e istruzioni fornite dall'utente. L'API utilizza un agente LLM per analizzare i dati di input e creare un workflow strutturato compatibile con Camunda.

L'API è stata sviluppata utilizzando **FastAPI**, che offre una documentazione automatica e interattiva grazie all'integrazione con **OpenAPI** e **Swagger UI**.

---

## Panoramica dell'API

- **Base URL**: `http://localhost:8000`
- **Versione API**: 1.0.0
- **Formato dei dati**: Tutte le richieste e le risposte sono in formato JSON.
- **Autenticazione**: Attualmente non è richiesta autenticazione.

---

## Autenticazione

L'API al momento non implementa alcun meccanismo di autenticazione. In un ambiente di produzione, si consiglia di implementare misure di sicurezza appropriate, come token API, OAuth2, JWT, ecc.

---

## Endpoint

### 1. Generazione del Workflow

- **Metodo**: `POST`
- **Endpoint**: `/generate-workflow`
- **Descrizione**: Genera un workflow strutturato basato sul `README` e sui media forniti dall'utente.
- **Tags**: `Workflow`

#### Dettagli della Richiesta

- **Headers**:
  - `Content-Type`: `application/json`

- **Body**: Un oggetto JSON che rispetta il modello `WorkflowInput`.

##### Modello `WorkflowInput`

- `readme` *(string, obbligatorio)*: Contiene le istruzioni generali e l'obiettivo del workflow.
- `media` *(object, obbligatorio)*: Raccolta di documenti, immagini e video associati.

---

#### Dettagli della Risposta

- **Codice di Stato**: `200 OK`
- **Body**: Un oggetto JSON che rispetta il modello `WorkflowOutput`.

##### Modello `WorkflowOutput`

- `tasks` *(array di oggetti, obbligatorio)*: Lista dei task generati nel workflow.

---

## Modelli di Dati

### 1. Modello di Input: `WorkflowInput`

```json
{
  "readme": "string",
  "media": {
    "documents": [
      {
        "id": "string",
        "name": "string",
        "description": "string",
        "type": "string",
        "value": "string"
      }
    ],
    "images": [
      {
        "id": "string",
        "name": "string",
        "description": "string",
        "type": "string",
        "value": "string"
      }
    ],
    "videos": [
      {
        "id": "string",
        "name": "string",
        "description": "string",
        "type": "string",
        "value": "string"
      }
    ]
  }
}
```

#### Descrizione dei Campi

- **readme** *(string, obbligatorio)*: Contiene le istruzioni generali e l'obiettivo del workflow.
  - *Esempio*: `"Questo workflow guida l'utente attraverso il montaggio di un mobile..."`

- **media** *(object, obbligatorio)*: Raccolta di media correlati al workflow.
  - **documents** *(array di oggetti)*: Lista di documenti.
    - **id** *(string, obbligatorio)*: Identificatore univoco del documento.
    - **name** *(string, obbligatorio)*: Nome descrittivo del documento.
    - **description** *(string, obbligatorio)*: Descrizione del documento.
    - **type** *(string, obbligatorio)*: Tipo di encoding del documento (es. `base64`).
    - **value** *(string, obbligatorio)*: Contenuto del documento codificato.
  - **images** *(array di oggetti)*: Lista di immagini.
    - *Stessi campi dei documenti*.
  - **videos** *(array di oggetti)*: Lista di video.
    - *Stessi campi dei documenti*.

---

### 2. Modello di Output: `WorkflowOutput`

```json
{
  "tasks": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "type": "string",
      "genericFields": {},
      "mediaContent": {
        "documents": [],
        "images": [],
        "videos": []
      },
      "script": {
        "language": "string",
        "code": "string"
      },
      "conditions": [],
      "variables": {}
    }
  ]
}
```

#### Descrizione dei Campi

- **tasks** *(array di oggetti, obbligatorio)*: Lista dei task generati nel workflow.

---

### 3. Modelli dei Task

I task possono essere di tre tipi principali:

1. **UserTask**
2. **ServiceTask**
3. **ExternalTask**

#### Campi Comuni a Tutti i Task

- **id** *(string, obbligatorio)*: Identificatore univoco del task.
- **name** *(string, obbligatorio)*: Nome descrittivo del task.
- **description** *(string, obbligatorio)*: Descrizione dettagliata delle attività richieste per il task.
- **type** *(string, obbligatorio)*: Tipo di task (`userTask`, `serviceTask`, `externalTask`).
- **genericFields** *(object)*: Campi generici per informazioni addizionali.
- **mediaContent** *(object)*: Media associati al task.
- **script** *(object)*: Script da eseguire nel task.
- **conditions** *(array di oggetti)*: Condizioni per determinare i flussi successivi.
- **variables** *(object)*: Variabili di processo utilizzabili durante l'esecuzione del task.

#### 3.1 UserTask

Campi aggiuntivi:

- **assignee** *(string)*: Utente assegnato al task.
- **candidateGroups** *(array di stringhe)*: Gruppi candidati per l'assegnazione del task.
- **formKey** *(string)*: Chiave del form associato al task.

#### 3.2 ServiceTask

Campi aggiuntivi:

- **implementation** *(string)*: Implementazione del task di servizio.
- **delegateExpression** *(string)*: Espressione del delegato per il task.
- **resultVariable** *(string)*: Nome della variabile dove salvare il risultato.

#### 3.3 ExternalTask

Campi aggiuntivi:

- **topicName** *(string, obbligatorio)*: Nome del topic per l'External Task.
- **workerId** *(string)*: ID del worker che esegue il task.
- **lockExpirationTime** *(string)*: Tempo di scadenza del lock in formato ISO 8601.
- **priority** *(integer)*: Priorità del task.
- **retries** *(integer)*: Numero di tentativi in caso di errore.
- **errorMessage** *(string)*: Messaggio di errore in caso di fallimento.
- **errorDetails** *(string)*: Dettagli aggiuntivi sull'errore.

---

## Esempi di Richieste e Risposte

### 1. Esempio di Richiesta

**Endpoint**: `/generate-workflow`

**Metodo**: `POST`

**Body**:

```json
{
  "readme": "Questo workflow guida l'utente attraverso il montaggio di un mobile, con verifiche di stabilità e controlli finali.",
  "media": {
    "documents": [
      {
        "id": "doc1",
        "name": "Manuale di Istruzioni",
        "description": "Contiene le istruzioni dettagliate per il montaggio del mobile.",
        "type": "base64",
        "value": "base64_encoded_document"
      }
    ],
    "images": [
      {
        "id": "img1",
        "name": "Diagramma dei Componenti",
        "description": "Illustrazione dei componenti del mobile.",
        "type": "base64",
        "value": "base64_encoded_image"
      }
    ],
    "videos": [
      {
        "id": "vid1",
        "name": "Tutorial di Montaggio",
        "description": "Video che mostra i passaggi per montare il mobile.",
        "type": "base64",
        "value": "base64_encoded_video"
      }
    ]
  }
}
```

### 2. Esempio di Risposta

**Codice di Stato**: `200 OK`

**Body**:

```json
{
  "tasks": [
    {
      "id": "task_1",
      "name": "Assemblare la Base",
      "description": "L'utente deve assemblare la base del mobile seguendo le istruzioni.",
      "type": "userTask",
      "assignee": "user_123",
      "candidateGroups": ["assemblers"],
      "formKey": "assembly_form",
      "genericFields": {},
      "mediaContent": {
        "documents": [
          {
            "id": "doc1",
            "name": "Manuale di Istruzioni",
            "description": "Contiene le istruzioni dettagliate per il montaggio del mobile.",
            "type": "base64",
            "value": "base64_encoded_document"
          }
        ],
        "images": [
          {
            "id": "img1",
            "name": "Diagramma dei Componenti",
            "description": "Illustrazione dei componenti del mobile.",
            "type": "base64",
            "value": "base64_encoded_image"
          }
        ],
        "videos": [
          {
            "id": "vid1",
            "name": "Tutorial di Montaggio",
            "description": "Video che mostra i passaggi per montare il mobile.",
            "type": "base64",
            "value": "base64_encoded_video"
          }
        ]
      },
      "script": null,
      "conditions": [
        {
          "conditionExpression": "${assemblyComplete == true}",
          "nextTaskId": "task_2"
        }
      ],
      "variables": {
        "assemblyComplete": {
          "type": "Boolean",
          "value": false
        }
      }
    }
  ]
}
```

---

## Codici di Stato HTTP

- **200 OK**: La richiesta è stata elaborata con successo e il workflow è stato generato.
- **400 Bad Request**: La richiesta contiene dati non validi o mancano campi obbligatori.
- **500 Internal Server Error**: Si è verificato un errore interno al server durante l'elaborazione della richiesta.

---

## Error Handling

In caso di errore, l'API restituisce una risposta con il codice di stato HTTP appropriato e un messaggio di errore dettagliato.

**Esempio di Errore 400**:

```json
{
  "detail": "Campo 'readme' mancante nella richiesta."
}
```

**Esempio di Errore 500**:

```json
{
  "detail": "Errore dall'API dell'agente: 503 Service Unavailable"
}
```

---

## Considerazioni Finali

- **Validazione dei Dati**: L'API utilizza Pydantic per la validazione dei dati di input e output. Assicurarsi di fornire tutti i campi obbligatori nel formato corretto.
- **Documentazione Interattiva**: È possibile accedere alla documentazione interattiva dell'API tramite Swagger UI all'indirizzo `http://localhost:8000/docs` o tramite Redoc all'indirizzo `http://localhost:8000/redoc`.
- **Estensibilità**: L'architettura è progettata per essere estensibile. È possibile aggiungere nuovi tipi di task o campi personalizzati secondo le esigenze.
- **Sicurezza**: Attualmente, l'API non implementa meccanismi di autenticazione o autorizzazione. Si consiglia di aggiungere misure di sicurezza in ambienti di produzione.

---

## Contatti e Supporto

Per ulteriori informazioni o supporto, contattare il team di sviluppo:

- **Email**: supporto@example.com
- **Telefono**: +39 0123 456789

---

# Appendice: Specifiche Tecniche dei Modelli

## Modello `MediaBase`

| Campo        | Tipo   | Obbligatorio | Descrizione                                                 |
|--------------|--------|--------------|-------------------------------------------------------------|
| id           | string | Sì           | Identificatore univoco del media.                           |
| name         | string | Sì           | Nome descrittivo del media.                                 |
| description  | string | Sì           | Descrizione del contenuto o dello scopo del media.          |
| type         | string | Sì           | Formato del media (es. `base64`).                           |
| value        | string | Sì           | Contenuto del media codificato (es. in Base64).             |

## Modello `TaskBase`

| Campo          | Tipo                     | Obbligatorio | Descrizione                                                  |
|----------------|--------------------------|--------------|--------------------------------------------------------------|
| id             | string                   | Sì           | Identificatore univoco del task.                             |
| name           | string                   | Sì           | Nome descrittivo del task.                                   |
| description    | string                   | Sì           | Descrizione dettagliata delle attività richieste per il task.|
| type           | string                   | Sì           | Tipo di task (`userTask`, `serviceTask`, `externalTask`).    |
| genericFields  | oggetto                  | No           | Campi generici per informazioni addizionali.                 |
| mediaContent   | oggetto `MediaContent`   | No           | Media associati al task.                                     |
| script         | oggetto `Script`         | No           | Script da eseguire nel task.                                 |
| conditions     | array di `Condition`     | No           | Condizioni per determinare i flussi successivi.              |
| variables      | oggetto                  | No           | Variabili di processo utilizzabili durante l'esecuzione.     |

## Modello `Condition`

| Campo                | Tipo   | Obbligatorio | Descrizione                                                  |
|----------------------|--------|--------------|--------------------------------------------------------------|
| conditionExpression  | string | Sì           | Espressione condizionale per il flusso (es. `${approved}`).  |
| nextTaskId           | string | Sì           | ID del task successivo se la condizione è soddisfatta.       |

---

# To Do
- **Endpoint per la validazione del workflow**: Verificare la correttezza e la coerenza del workflow generato.
- **Endpoint per l'aggiornamento dei task**: Permettere l'aggiornamento o la modifica dei task esistenti.
- **Endpoint per l'eliminazione del workflow**: Consentire la rimozione di workflow non più necessari.
