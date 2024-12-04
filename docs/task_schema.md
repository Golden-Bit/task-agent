## Descrizione Generale

Questa struttura dati consente la creazione di task per Camunda basati su input complessi, tra cui documenti, media, e istruzioni fornite dall'utente. Utilizzando un file `README` centrale per specificare l'obiettivo del workflow e linee guida dettagliate, ogni media e documento è corredato da un nome e una descrizione che forniscono all'agente tutte le informazioni per generare workflow strutturati e adattivi.

L’agente basato su LLM analizza il `README` e i contenuti multimediali per costruire autonomamente un workflow composto da task correlati e collegati tramite condizioni di movimento. Lo scopo è permettere la generazione automatizzata di workflow complessi e personalizzati, ottimizzando il processo di costruzione e organizzazione.

---

## Input Atteso

L'input fornito dall'utente per la generazione automatica del workflow è strutturato come segue:

1. **File `README` Centrale**:
   - Contiene le istruzioni generali, linee guida, e l’obiettivo generale del workflow.
   - Specifica i passaggi principali e le direttive che l’agente dovrà considerare per creare un workflow ottimale.

2. **Documenti e Media**:
   - Una raccolta di documenti, immagini e video, ciascuno corredato da informazioni descrittive:
     - **ID**: Identificatore univoco per il media.
     - **Nome**: Titolo descrittivo che facilita il riconoscimento del contenuto.
     - **Descrizione**: Dettagli sul contenuto o sullo scopo del media.
     - **Contenuto**: Il contenuto vero e proprio codificato in Base64 (per immagini, video o documenti).

### Esempio di Input

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

---

## Output Generato

L'output è una **lista di task** strutturati in un workflow compatibile con Camunda. Ogni task include:

- I dettagli operativi necessari per l'esecuzione.
- Collegamenti ai documenti e media specificati in input.
- Condizioni di movimento generate autonomamente dall’agente, basate sulle descrizioni contenute nel file `README` e nei media forniti.

---

## Struttura Dati Comuni a Tutti i Task

I campi comuni per ciascun task includono descrizioni, media associati, e la logica condizionale per la transizione tra task, che viene dedotta dall’agente durante la generazione del workflow. Ogni tipo di task ha campi specifici, ma tutti includono la seguente struttura base.

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "type": "string",
  "genericFields": {
    "field1": {
      "type": "string",
      "value": "any"
    },
    "field2": {
      "type": "string",
      "value": "any"
    }
  },
  "mediaContent": {
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
    ],
    "documents": [
      {
        "id": "doc1",
        "name": "Manuale di Istruzioni",
        "description": "Contiene le istruzioni dettagliate per il montaggio del mobile.",
        "type": "base64",
        "value": "base64_encoded_document"
      }
    ]
  },
  "script": {
    "language": "string",
    "code": "string"
  },
  "conditions": [
    {
      "conditionExpression": "string",
      "nextTaskId": "string"
    }
  ],
  "variables": {
    "variableName": {
      "type": "String",
      "value": "any"
    }
  }
}
```

### Descrizione dei Campi Comuni

- **id**: Identificatore univoco del task.
- **name**: Nome descrittivo del task.
- **description**: Descrizione dettagliata delle attività richieste per il task.
- **type**: Tipo di task (es. "userTask", "serviceTask", "externalTask").
- **genericFields**: Campi generici in formato chiave-valore per informazioni addizionali.
- **mediaContent**: Raccolta di immagini, video e documenti associati al task.
  - **id**: Identificatore univoco del media.
  - **name**: Nome descrittivo del media.
  - **description**: Descrizione del contenuto o dello scopo del media.
  - **type**: Formato (ad esempio, `base64`).
  - **value**: Contenuto del media codificato in Base64.
- **script**: Sezione per l’esecuzione di uno script, con il campo **language** per il linguaggio e **code** per il codice.
- **conditions**: Array di condizioni per determinare i flussi successivi. Ogni condizione contiene:
  - **conditionExpression**: Espressione condizionale che stabilisce se procedere al task successivo.
  - **nextTaskId**: ID del task successivo se la condizione è soddisfatta.
- **variables**: Variabili di processo utilizzabili durante l'esecuzione del task.

---

## Struttura Dati per Tipi di Task Specifici

### 1. **Struttura Dati per `User Task`**

Uno **User Task** richiede l’interazione diretta con l’utente e include campi per l'assegnazione a specifici utenti o gruppi.

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "type": "userTask",
  "assignee": "string",
  "candidateGroups": ["string"],
  "formKey": "string",
  "genericFields": { /* vedi sopra */ },
  "mediaContent": { /* vedi sopra */ },
  "script": null,
  "conditions": [ /* vedi sopra */ ],
  "variables": { /* vedi sopra */ }
}
```

### 2. **Struttura Dati per `Service Task`**

Un **Service Task** esegue azioni automatiche definite dall’agente o dall’utente.

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "type": "serviceTask",
  "implementation": "string",
  "delegateExpression": "string",
  "script": {
    "language": "string",
    "code": "string"
  },
  "resultVariable": "string",
  "genericFields": { /* vedi sopra */ },
  "mediaContent": { /* vedi sopra */ },
  "conditions": [ /* vedi sopra */ ],
  "variables": { /* vedi sopra */ }
}
```

### 3. **Struttura Dati per `External Task`**

Un **External Task** è destinato all’esecuzione da parte di un servizio esterno.

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "type": "externalTask",
  "topicName": "string

",
  "workerId": "string",
  "lockExpirationTime": "datetime",
  "priority": "integer",
  "retries": "integer",
  "errorMessage": "string",
  "errorDetails": "string",
  "genericFields": { /* vedi sopra */ },
  "mediaContent": { /* vedi sopra */ },
  "script": null,
  "conditions": [ /* vedi sopra */ ],
  "variables": { /* vedi sopra */ }
}
```

---

## Funzionamento dell'Agente LLM per la Generazione del Workflow

L’agente LLM analizza i documenti e il file `README` per:

1. Estrarre e interpretare le informazioni contenute nei media e nei documenti.
2. Identificare l’obiettivo principale del workflow e definire i passaggi necessari.
3. Creare i task automaticamente, assegnando media e documenti ai task pertinenti.
4. Stabilire autonomamente le condizioni di movimento per collegare i task, generando così un flusso logico.

Questo approccio permette di costruire workflow complessi e personalizzati, adattandosi dinamicamente alle istruzioni fornite.

