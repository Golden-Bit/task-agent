## 1. Documentazione dei due Schemi

### 1.1 Schema della **Lista di File** (concettuale)

**Struttura generale (in JSON)**

```json
[
  {
    "session_id": "<session_id_string>",
    "file_id": "<file_id_string>",
    "file_type": "<pdf, docx, mp4, jpg etc...>",
    "source_file": "<source_file_id_string>",
    "title": "<title_string>",
    "description": "<description_string>",
    "b64_content": "<b64_string>"
  },
  {
    "session_id": "<session_id_string>",
    "file_id": "<file_id_string>",
    "file_type": "<pdf, docx, mp4, jpg etc...>",
    "source_file": "<source_file_id_string>",
    "title": "<title_string>",
    "description": "<description_string>",
    "b64_content": "<b64_string>"
  },
  ...
]

```

**Campi principali**

-   **session_id**: Identificatore univoco della sessione di elaborazione AI.
-   **file_id**: Identificatore univoco del file.
-   **file_type**: Tipologia del file (es. _pdf_, _docx_, _mp4_, _jpg_, ecc.).
-   **source_file**: ID del file sorgente da cui questo file deriva (utile per conversioni, frammentazioni, ecc.).
-   **title**: Titolo descrittivo del contenuto.
-   **description**: Descrizione testuale del contenuto.
-   **b64_content**: Stringa Base64 con il contenuto binario del file.

#### Considerazioni d’uso

1.  **Lista di file**: Il sistema AI può produrre numerosi file di natura diversa, tutti elencati in questo array.
2.  **Riferimenti incrociati**: Se un file è estratto o derivato da un altro, `source_file` chiarisce la provenienza.
3.  **Session ID**: Permette di raggruppare i file appartenenti a una stessa elaborazione.

----------

### 1.2 Schema dei **Workflow** (concettuale)

**Struttura generale (in JSON)**

```json
{
  "session_id": "<session_id_string>",
  "workflows": [
    {
      "id": "<workflow_id_string>",
      "title": "<titolo_del_workflow>",
      "description": "<descrizione_del_workflow>",
      "media": [
        {
          "file_id": "<file_id_string>",
          "file_type": "<pdf, docx, mp4, jpg etc...>",
          "source_file": "<source_file_id_string>",
          "title": "<title_string>",
          "description": "<description_string>"
        },
        {
          "file_id": "<file_id_string>",
          "file_type": "<pdf, docx, mp4, jpg etc...>",
          "source_file": "<source_file_id_string>",
          "title": "<title_string>",
          "description": "<description_string>"
        }
        ...
      ],
      "workflow": [
        {
          "id": "<task_id_string>",
          "name": "<nome_della_task>",
          "description": "<descrizione_della_task>",
          "type": "<tipologia_task>",
          "assignee": "<utente_assegnato>",
          "candidateGroups": [
            "<gruppo_candidato1>",
            "<gruppo_candidato2>"
          ],
          "formKey": "<form_key_string>",
          "genericFields": {},
          "mediaContent": {
            "documents": [
              {
                "file_id": "<file_id_string>",
                "file_type": "<pdf, docx, etc...>",
                "source_file": "<source_file_id_string>",
                "title": "<title_string>",
                "description": "<description_string>"
              },
              ...
            ],
            "images": [
              {
                "file_id": "<file_id_string>",
                "file_type": "<jpg, png, etc...>",
                "source_file": "<source_file_id_string>",
                "title": "<title_string>",
                "description": "<description_string>"
              },
              ...
            ],
            "videos": [
              {
                "file_id": "<file_id_string>",
                "file_type": "<mp4, mkv, etc...>",
                "source_file": "<source_file_id_string>",
                "title": "<title_string>",
                "description": "<description_string>"
              },
              ...
            ]
          },
          "script": null,
          "conditions": [],
          "variables": {}
        },
        ...
      ]
    },
    ...
  ]
}

```

**Campi principali**

-   **session_id**: Deve corrispondere a quello nella Lista di File per mantenere coerenza.
-   **workflows**: Array di uno o più workflow.
    -   **id**: Identificatore del singolo workflow.
    -   **title**: Nome o titolo descrittivo.
    -   **description**: Descrizione testuale dell’obiettivo o del contesto del workflow.
    -   **media**: Elenco di file (riferiti tramite `file_id`) disponibili a livello globale del workflow.
    -   **workflow**: Sequenza di task:
        -   **id**: Identificatore univoco della task.
        -   **name**: Nome della task.
        -   **description**: Descrizione di cosa fare in questa task.
        -   **type**: Tipo di attività (es. _userTask_, _scriptTask_, ecc.).
        -   **assignee**: Utente o ruolo designato.
        -   **candidateGroups**: Elenco di gruppi abilitati a svolgere la task.
        -   **formKey**: Riferimento a un eventuale modulo di input.
        -   **genericFields**: Oggetto generico per campi personalizzati.
        -   **mediaContent**: File specifici per la task, suddivisi in `documents`, `images`, `videos`.
        -   **script**: Se presente, codice eseguibile dalla task (altrimenti `null`).
        -   **conditions**: Condizioni o regole per passare a task successive.
        -   **variables**: Variabili di contesto (valori di configurazione, parametri, ecc.).

#### Considerazioni d’uso

1.  **Media a due livelli**:
    -   A livello di **workflow** (`media`): risorse condivise da tutte le task di quello specifico flusso.
    -   A livello di **task** (`mediaContent`): risorse rilevanti solo per un’istruzione specifica.
2.  **Riferimenti incrociati**: I `file_id` usati nei workflow devono essere presenti nella Lista di File.
3.  **Struttura estensibile**: Grazie a `genericFields` e `variables`, è possibile aggiungere metadati personalizzati senza infrangere lo schema.

----------

## 2. Schemi in YAML (Standard JSON Schema Draft-07)

Di seguito, forniamo la **versione YAML** di entrambi gli schemi, conforme allo **standard JSON Schema (Draft-07)**, così da poter validare formalmente i dati prodotti o elaborati.

### 2.1 Schema “Lista di File” (FileListSchema)

```yaml
$schema: "http://json-schema.org/draft-07/schema#"
title: "FileListSchema"
type: "array"

items:
  type: object
  properties:
    session_id:
      type: string
      description: "Stringa univoca per la sessione di elaborazione AI."
    file_id:
      type: string
      description: "Stringa univoca per identificare il file."
    file_type:
      type: string
      description: "Tipologia di file (pdf, docx, mp4, jpg, ecc.)."
    source_file:
      type: string
      description: "File sorgente da cui è stato derivato questo output."
    title:
      type: string
      description: "Titolo descrittivo del contenuto."
    description:
      type: string
      description: "Descrizione testuale del contenuto."
    b64_content:
      type: string
      description: "Contenuto del file codificato in Base64."
  required:
    - session_id
    - file_id
    - file_type
    - source_file
    - title
    - description
    - b64_content

description: >
  Rappresentazione di un elenco di file generati o elaborati da un sistema
  di intelligenza artificiale, completi di informazioni testuali e contenuto
  in Base64.

```

**Caratteristiche principali**

-   La radice è un `array` di oggetti, in linea con la struttura JSON concettuale.
-   Ogni file deve avere i campi `session_id`, `file_id`, `file_type`, `source_file`, `title`, `description` e `b64_content`.

----------

### 2.2 Schema “Workflow” (WorkflowSchema)

```yaml
$schema: "http://json-schema.org/draft-07/schema#"
title: "WorkflowSchema"
type: object

properties:
  session_id:
    type: string
    description: "Stringa univoca per la sessione di elaborazione (identico al session_id della lista di file)."
  workflows:
    type: array
    description: "Elenco di workflow generati dal sistema AI."
    items:
      type: object
      properties:
        id:
          type: string
          description: "Identificatore univoco del workflow."
        title:
          type: string
          description: "Titolo descrittivo del workflow."
        description:
          type: string
          description: "Descrizione generale del workflow."
        media:
          type: array
          description: "File associati a livello globale per il workflow."
          items:
            type: object
            properties:
              file_id:
                type: string
              file_type:
                type: string
              source_file:
                type: string
              title:
                type: string
              description:
                type: string
            required:
              - file_id
              - file_type
              - source_file
              - title
              - description
        workflow:
          type: array
          description: "Sequenza di task che compongono il workflow."
          items:
            type: object
            properties:
              id:
                type: string
                description: "Identificatore univoco della task."
              name:
                type: string
                description: "Nome della task."
              description:
                type: string
                description: "Descrizione dettagliata della task."
              type:
                type: string
                description: "Tipologia di task (es. userTask, scriptTask...)."
              assignee:
                type: string
                description: "Utente/ruolo assegnato alla task."
              candidateGroups:
                type: array
                description: "Lista di gruppi candidati alla task."
                items:
                  type: string
              formKey:
                type: string
                description: "Riferimento a un modulo di input/maschera."
              genericFields:
                type: object
                description: "Struttura generica per campi aggiuntivi."
              mediaContent:
                type: object
                description: "Contenuto multimediale specifico per la singola task."
                properties:
                  documents:
                    type: array
                    items:
                      type: object
                      properties:
                        file_id:
                          type: string
                        file_type:
                          type: string
                        source_file:
                          type: string
                        title:
                          type: string
                        description:
                          type: string
                      required:
                        - file_id
                        - file_type
                        - source_file
                        - title
                        - description
                  images:
                    type: array
                    items:
                      type: object
                      properties:
                        file_id:
                          type: string
                        file_type:
                          type: string
                        source_file:
                          type: string
                        title:
                          type: string
                        description:
                          type: string
                      required:
                        - file_id
                        - file_type
                        - source_file
                        - title
                        - description
                  videos:
                    type: array
                    items:
                      type: object
                      properties:
                        file_id:
                          type: string
                        file_type:
                          type: string
                        source_file:
                          type: string
                        title:
                          type: string
                        description:
                          type: string
                      required:
                        - file_id
                        - file_type
                        - source_file
                        - title
                        - description
                required:
                  - documents
                  - images
                  - videos
              script:
                type: [string, "null"]
                description: "Campo opzionale per eventuali script da eseguire."
              conditions:
                type: array
                description: "Lista di condizioni per passaggio tra task."
                items: {}
              variables:
                type: object
                description: "Variabili di contesto per la task."
            required:
              - id
              - name
              - description
              - type
              - assignee
              - candidateGroups
              - formKey
              - genericFields
              - mediaContent
              - script
              - conditions
              - variables
      required:
        - id
        - title
        - description
        - media
        - workflow

required:
  - session_id
  - workflows

description: >
  Rappresentazione di uno o più workflow (contenuti in un array),
  ciascuno composto da task. Ogni workflow fa riferimento a media
  globali e a contenuti associati a singole task.

```

**Caratteristiche principali**

-   Radice di tipo `object` con proprietà `session_id` e `workflows`.
-   Ogni `workflow` è un oggetto con `id`, `title`, `description`, `media`, `workflow` (array di task).
-   Ogni task possiede campi specifici (`id`, `name`, `description`, `type`, ecc.) e una sezione dedicata (`mediaContent`) per file documenti, immagini e video.
-   I campi `required` assicurano che tutti i dati indispensabili siano presenti.

----------
