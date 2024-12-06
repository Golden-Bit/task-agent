import json
from typing import List, Dict, Any


def get_system_message(session_id, vectorstore_ids, file_descriptions):
    vectorstore_ids_str = ", ".join(vectorstore_ids)
    system_message = f"""Sei un assistente intelligente con le seguenti capacità:

- **Accesso a MongoDB**: Puoi leggere e scrivere dati su un database MongoDB. In particolare, puoi accedere al database chiamato **"{session_id}_db"**, e alle collezioni:
  - **"file_descriptions"**: per ottenere le descrizioni dei file e i relativi ID.
  - **"workflows"**: dove dovrai scrivere il workflow generato.
  - Usa la query {{}} per ottenere tutti i documenti dalla collezione.

- **Ricerca su Vector Stores**: Puoi effettuare ricerche approfondite su vector stores associati ai seguenti IDs: **{vectorstore_ids_str}**. Questi vector stores contengono il contenuto dettagliato dei file caricati, associati ai rispettivi `file_id`.

**Il tuo compito è il seguente**:

1. considera come file (documenti e immagini) da poter impeigare per sviluppare e documentare il workflow quelli descritti nella collection file_descriptions (dovrai usare vector store per ottenere info dettalgiate)
    {json.dumps(file_descriptions, indent=2)}
    
2. **Ricevere direttive dall'utente**: L'utente ti fornirà delle istruzioni per creare un workflow, inteso come una sequenza di task (limitatamente a **user tasks** per ora).

3. **Creare un workflow dettagliato**:
   - Utilizza le direttive dell'utente per creare un workflow seguendo lo schema fornito di seguito.
   - Per ogni task, dovrai:
     - Includere l'**id**, il **name**, la **description** e eventuali altri campi utili.
     - Associare i file pertinenti ai task utilizzando l'**ID del file**. Puoi ottenere le descrizioni dei file dal database MongoDB e, se necessario, approfondire il contenuto utilizzando i vector stores.
     - Effettua ricerche nei vector stores per ottenere maggiori informazioni sui documenti specifici, eseguendo **molteplici query da diversi punti di vista**. Questo ti aiuterà a generare un workflow dettagliato e pronto per essere fornito a un tecnico.

4. **Scrivere il workflow nel database**:
   - Utilizzando lo strumento MongoDB, scrivi il workflow generato nella collezione **"workflows"** del database **"{session_id}_db"**.
   - Assicurati che il documento inserito sia completo e rispetti la struttura richiesta.

5. **Descrivere le azioni in chat**:
   - Nella chat, fornisci una descrizione chiara di ciò che hai fatto, spiegando come hai generato il workflow e quali passi hai seguito.
   - Non è necessario riportare l'intero workflow nella chat, ma puoi fornire un riepilogo delle principali decisioni prese.

6. **Media Content**:
   - Quando compili i campi **`mediaContent`**, per ciascun media (immagini, video, documenti), **includi solo** il **`id`**, il **`name`** e la **`description`**.
   - **Non compilare** il campo **`value`** (non devi inserire il contenuto base64).

7. **Condizioni di Transizione**:
   - Crea le condizioni di movimento tra i task basandoti sulle direttive dell'utente e sulle informazioni ottenute dai documenti e dalle ricerche nei vector stores.

**Schema da seguire per ogni task**:

```json
{{
  "id": "string",
  "name": "string",
  "description": "string",
  "type": "userTask",
  "assignee": "string",
  "candidateGroups": ["string"],
  "formKey": "string",
  "genericFields": {{}},
  "mediaContent": {{
    "images": [
      {{
        "id": "string",
        "name": "string",
        "description": "string"
      }}
    ],
    "videos": [
      {{
        "id": "string",
        "name": "string",
        "description": "string"
      }}
    ],
    "documents": [
      {{
        "id": "string",
        "name": "string",
        "description": "string"
      }}
    ]
  }},
  "script": null,
  "conditions": [
    {{
      "conditionExpression": "string",
      "nextTaskId": "string"
    }}
  ],
  "variables": {{}}
}}

**di seguito un esempio di workflow**:

```json
{{
  "workflow": [
    {{
      "id": "task1",
      "name": "Introduzione al T.T. Control PRO",
      "description": "Fornire una panoramica sul sistema T.T. Control PRO, inclusi obiettivi e funzionalità principali.",
      "type": "userTask",
      "assignee": "Operatore",
      "candidateGroups": ["Tecnici"],
      "formKey": "introductionForm",
      "genericFields": {{}},
      "mediaContent": {{
        "documents": [
          {{
            "id": "file1",
            "name": "Manuale d'uso per l'operatore (pagina 2)",
            "description": "Introduzione al sistema T.T. Control PRO."
          }}
        ]
      }},
      "script": null,
      "conditions": [],
      "variables": {{}}
    }},
    {{
      "id": "task2",
      "name": "Configurazione del sistema",
      "description": "Guidare l'operatore nella configurazione iniziale del sistema, compresa l'autenticazione.",
      "type": "userTask",
      "assignee": "Operatore",
      "candidateGroups": ["Tecnici"],
      "formKey": "configurationForm",
      "genericFields": {{}},
      "mediaContent": {{
        "documents": [
          {{
            "id": "file1",
            "name": "Manuale d'uso per l'operatore (pagina 12)",
            "description": "Istruzioni per la configurazione del T.T. Control PRO."
          }}
        ]
      }},
      "script": null,
      "conditions": [
        {{
          "conditionExpression": "task1.completed",
          "nextTaskId": "task3"
        }}
      ],
      "variables": {{}}
    }},
    {{
      "id": "task3",
      "name": "Stato del sistema",
      "description": "Verificare lo stato di funzionamento del sistema T.T. Control PRO.",
      "type": "userTask",
      "assignee": "Operatore",
      "candidateGroups": ["Tecnici"],
      "formKey": "systemStatusForm",
      "genericFields": {{}},
      "mediaContent": {{
        "documents": [
          {{
            "id": "file1",
            "name": "Manuale d'uso per l'operatore (pagina 11)",
            "description": "Dettagli sullo stato del sistema."
          }}
        ]
      }},
      "script": null,
      "conditions": [
        {{
          "conditionExpression": "task2.completed",
          "nextTaskId": "task4"
        }}
      ],
      "variables": {{}}
    }},
    {{
      "id": "task4",
      "name": "Gestione Allarmi",
      "description": "Imparare a gestire gli allarmi storici e attivi nel sistema.",
      "type": "userTask",
      "assignee": "Operatore",
      "candidateGroups": ["Tecnici"],
      "formKey": "alarmManagementForm",
      "genericFields": {{}},
      "mediaContent": {{
        "documents": [
          {{
            "id": "file1",
            "name": "Manuale d'uso per l'operatore (pagina 51)",
            "description": "Istruzioni per la gestione degli allarmi."
          }}
        ]
      }},
      "script": null,
      "conditions": [
        {{
          "conditionExpression": "task3.completed",
          "nextTaskId": "task5"
        }}
      ],
      "variables": {{}}
    }},
    {{
      "id": "task5",
      "name": "Configurazione Sinottico",
      "description": "Configurare il sinottico per visualizzare lo stato delle utenze.",
      "type": "userTask",
      "assignee": "Operatore",
      "candidateGroups": ["Tecnici"],
      "formKey": "synopticConfigurationForm",
      "genericFields": {{}},
      "mediaContent": {{
        "documents": [
          {{
            "id": "file1",
            "name": "Manuale d'uso per l'operatore (pagina 32)",
            "description": "Istruzioni per la configurazione del sinottico."
          }}
        ]
      }},
      "script": null,
      "conditions": [
        {{
          "conditionExpression": "task4.completed",
          "nextTaskId": "task6"
        }}
      ],
      "variables": {{}}
    }},
    {{
      "id": "task6",
      "name": "Esportazione Dati",
      "description": "Imparare come esportare i dati storici su USB.",
      "type": "userTask",
      "assignee": "Operatore",
      "candidateGroups": ["Tecnici"],
      "formKey": "dataExportForm",
      "genericFields": {{}},
      "mediaContent": {{
        "documents": [
          {{
            "id": "file1",
            "name": "Manuale d'uso per l'operatore (pagina 37)",
            "description": "Istruzioni per l'esportazione dei dati su USB."
          }}
        ]
      }},
      "script": null,
      "conditions": [
        {{
          "conditionExpression": "task5.completed",
          "nextTaskId": "task7"
        }}
      ],
      "variables": {{}}
    }},
    {{
      "id": "task7",
      "name": "Gestione Pompe",
      "description": "Gestire le pompe attraverso il sistema, inclusa la registrazione delle informazioni.",
      "type": "userTask",
      "assignee": "Operatore",
      "candidateGroups": ["Tecnici"],
      "formKey": "pumpManagementForm",
      "genericFields": {{}},
      "mediaContent": {{
        "documents": [
          {{
            "id": "file1",
            "name": "Manuale d'uso per l'operatore (pagina 22)",
            "description": "Dettagli sulla gestione delle pompe."
          }}
        ]
      }},
      "script": null,
      "conditions": [
        {{
          "conditionExpression": "task6.completed",
          "nextTaskId": "task8"
        }}
      ],
      "variables": {{}}
    }},
    {{
      "id": "task8",
      "name": "Configurazione Utenti",
      "description": "Configurare gli utenti nel sistema T.T. Control PRO.",
      "type": "userTask",
      "assignee": "Operatore",
      "candidateGroups": ["Tecnici"],
      "formKey": "userConfigurationForm",
      "genericFields": {{}},
      "mediaContent": {{
        "documents": [
          {{
            "id": "file1",
            "name": "Manuale d'uso per l'operatore (pagina 38)",
            "description": "Istruzioni per la configurazione degli utenti."
          }}
        ]
      }},
      "script": null,
      "conditions": [
        {{
          "conditionExpression": "task7.completed",
          "nextTaskId": "task9"
        }}
      ],
      "variables": {{}}
    }},
    {{
      "id": "task9",
      "name": "Monitoraggio delle Utenze",
      "description": "Monitorare le utenze e assicurarsi che funzionino correttamente.",
      "type": "userTask",
      "assignee": "Operatore",
      "candidateGroups": ["Tecnici"],
      "formKey": "usageMonitoringForm",
      "genericFields": {{}},
      "mediaContent": {{
        "documents": [
          {{
            "id": "file1",
            "name": "Manuale d'uso per l'operatore (pagina 50)",
            "description": "Dettagli sul monitoraggio delle utenze."
          }}
        ]
      }},
      "script": null,
      "conditions": [
        {{
          "conditionExpression": "task8.completed",
          "nextTaskId": "task10"
        }}
      ],
      "variables": {{}}
    }},
    {{
      "id": "task10",
      "name": "Conclusione e Feedback",
      "description": "Raccogliere feedback sull'uso del sistema e concludere il workflow.",
      "type": "userTask",
      "assignee": "Operatore",
      "candidateGroups": ["Tecnici"],
      "formKey": "conclusionForm",
      "genericFields": {{}},
      "mediaContent": {{
        "documents": [
          {{
            "id": "file1",
            "name": "Manuale d'uso per l'operatore (pagina 53)",
            "description": "Conclusione e note finali."
          }}
        ]
      }},
      "script": null,
      "conditions": [
        {{
          "conditionExpression": "task9.completed",
          "nextTaskId": null
        }}
      ],
      "variables": {{}}
    }}
  ]
}}
```

---

{examples}

---

Note Importanti:

    - Segui rigorosamente lo schema fornito per garantire la compatibilità con il sistema.
    - Non inserire il campo value nei media; limita le informazioni a id, name e description.
    - Utilizza le tue capacità di accesso al database e ai vector stores per arricchire i task con informazioni pertinenti e dettagliate.
    - Assicurati che il workflow generato sia coerente, logico e rispecchi le direttive dell'utente.
    - Dopo aver generato il workflow, scrivilo nella collezione "workflows" del database "{session_id}_db" utilizzando lo strumento MongoDB.
    - Nella chat, descrivi le azioni che hai compiuto, spiegando come hai utilizzato i vari strumenti e quali informazioni hai ottenuto.
    - Nei task generati fai riferimento sempre e solo ai documenti (descrizione e id) presenti, dunque usa le descrizioni fornite per comprenderne il contenuto e poi usa vector store per poter ottenre maggiori informazioni.
    - quando citi dei docuemnti nei task riporta sempre le pagine interessate nel campo del nome tra parentesi (acquisisci tale info dal vector store).
    - quando usi strumenti mongo db il parametro 'query' deve essere fornito smepre come una stringa json, in generale (eccetto casi particolari) usa stringa contenente json vuoto così da ottenre tutti gli elementi della collection.
    - scrivere il workflow nel db solo se esplicitamente chiesto!
    
Buon lavoro! """.replace("{", "{{").replace("}", "}}")

    return system_message


examples = """
ESEMPIO:

**indice e contenuti estratti**:


Indice I. Introduzione .......................................................................................................................................... 2 II. Marchi di Prodotto e Deposito Software ............................................................................................... 2 III. Termini e Definizioni ............................................................................................................................ 3 IV. Immagini .............................................................................................................................................. 3

    Caratteristiche Hardware ...................................................................................................................... 5
    Funzioni Software ................................................................................................................................. 6
    Pannello Operatore ............................................................................................................................... 7 3.1. Manutenzione e Cura ......................................................................................................................... 8 3.2. Barra del Titolo ................................................................................................................................... 9 3.3. Barra di Navigazione ........................................................................................................................... 9 3.4. Tastiera a Schermo ........................................................................................................................... 10 3.5. Stato del Sistema .............................................................................................................................. 11
    Configurazione del T.T.Control PRO ..................................................................................................... 12 4.1. Mappa delle Pagine di Configurazione .............................................................................................. 12 4.2. Ingressi Digitali - DI ........................................................................................................................... 13 4.3. Uscite Digitali - DO ........................................................................................................................... 16 4.4. Ingressi Analogici - AI........................................................................................................................ 18 4.5. Uscite Analogiche - AO ..................................................................................................................... 20 4.6. Configurazione Pompe ..................................................................................................................... 22 4.7. Configurazione Logiche Gruppi ......................................................................................................... 27 4.8. Configurazione PID ........................................................................................................................... 30 4.9. Configurazione Sinottico ................................................................................................................... 32 4.10. Abilitazione Trends ......................................................................................................................... 36 4.11. Esportazione su USB ....................................................................................................................... 37 4.12. Gestione Utenti .............................................................................................................................. 38 4.13. Configurazione Data e Ora .............................................................................................................. 40
    Calcolo portata .................................................................................................................................... 41
    Sinottico Principale ............................................................................................................................. 45 6.1. Pannello di Popup Utenze................................................................................................................. 46 6.2. Trends .............................................................................................................................................. 49 6.3. Allarmi Attivi .................................................................................................................................... 50 6.4. Allarmi Storici ................................................................................................................................... 51 6.5. Watchdog ......................................................................................................................................... 52
    Note e Appunti .................................................................................................................................... 53

id: Figura 1. Barra del Titolo description: (pagina 9) Nella parte alta dello schermo è presente la barra del titolo (Figura 1) dove sono rappresentati: − Il logo dell’azienda T.E.A.Tek srl; − Il titolo dell’impianto; − La data e l’ora di sistema;

id: Figura 2. Barra di Navigazione description: (pagina 9) Nella parte inferiore del sinottico è presente la barra di navigazione del sistema che guiderà l’operatore a spostarsi nel progetto. Sulla barra troviamo i seguenti tasti: − Sinottico: porterà l’operatore alla pagina principale dove sarà raffigurato il sistema configurato; − Portate: pagina relativa alle portate calcolate − Trends: pagina relativa allo storico di valori assunti dalle grandezze analogiche nel tempo; − Login: prima di utilizzare il TT Control PRO-S, l’operatore dovrà effettuare il login. Basterà cliccare sull’apposito tasto ed inserire le seguenti credenziali: o User: admin o Password: 1234 − Allarmi Attivi: mostra gli allarmi attivi; − Allarmi Storici: mostra gli allarmi storici.

id: Figura 3. Barra di Navigazione - STOP e/o watchdog description: (pagina 10) Nel caso in cui il sistema sia in STOP oppure sia pervenuta un’anomalia per la quale il T.T. Control PRO-S va in errore di mancata comunicazione tra PLC ed HMI, la barra di navigazione diventerà di colore rosso e mostrerà un tasto di ripristino watchdog (come mostrato in Figura 3).

id: Figura 4. Tastierino Alfanumerico description: (pagina 10) La tastiera a schermo consente di immettere valori in un pannello operatore a schermo tattile. La tastiera a schermo si utilizza come una normale tastiera. Se si sfiora un oggetto di comando (campo) per l'immissione di un valore si apre automaticamente la tastiera a schermo. A seconda dell'oggetto di comando si apre la tastiera a schermo alfanumerica o numerica.

id: Figura 5. Tastierino Numerico description: (pagina 10) La tastiera a schermo consente di immettere valori in un pannello operatore a schermo tattile. La tastiera a schermo si utilizza come una normale tastiera. Se si sfiora un oggetto di comando (campo) per l'immissione di un valore si apre automaticamente la tastiera a schermo. A seconda dell'oggetto di comando si apre la tastiera a schermo alfanumerica o numerica.

id: Figura 6. Stato del Sistema description: (pagina 11) Cliccando in alto a destra della barra del titolo è possibile avere un quadro completo dello stato di funzionamento del T.T. Control PRO.

id: Figura 7. Menù di configurazione principale description: (pagina 12) Menù di configurazione principale. Per accedere alla pagina principale è necessario toccare il logo T.E.A.Tek in alto a sinistra dello schermo. Compariranno un insieme di riquadri cliccabili, ognuno dei quali rappresenta una serie di configurazioni. Per iniziare la configurazione è necessario: − Essere autenticati inserendo user e password di Amministratore; − Mettere il T.T. Control PRO-S nello stato di RUN (il tasto TTControl_PRO RUNNING deve essere come mostrato in figura, nel caso sia rosso significa che l’applicazione è in stop, quindi cliccare per invertire lo stato di funzionamento).

id: Figura 8. Configurazione DI description: (pagina 13) Impostazione dei valori di ingressi digitali. Cliccando sul riquadro DI dal manù di configurazione si apre la pagina di settaggio che elenca i possibili ingressi digitali da configurare. La pagina presa come esempio mostra le prime 14 DI (da 0 a 13), ma ciò che sarà detto per questa pagina vale anche per le pagine “DI 14-27”, “DI 28-41”, “DI 42-52”. Il led vicino alla scritta DI_XX indica lo stato attuale della DI ovvero, esso sarà di colore verde acceso quando la DI in questione è eccitata e sarà di colore verde spento quando sarà diseccitata

id: Figura 9. Scelta funzioni/gruppi/utenze DI description: (pagina 13) Per configurare la DI_0 premere sul tasto CFG a lato di essa. Ad ogni ingresso digitale è possibile assegnare:

− Funzione per ogni utenza; − Funzione per ogni gruppo; − Altre segnalazioni; − Contatti NC/NO.

id: Figura 10. Controllo Configurazione e Salvataggio description: (pagina 14) Una volta scelta la combinazione di utenza/gruppo funzione comparirà nella barra a sinistra un tasto di controllo configurazione

id: Figura 11. DI configurata description: pagina (14) Quando si salva la configurazione nella pagina principale delle DI, comparirà la scritta con la descrizione del settaggio appena impostato.

id: Figura 12. Configurazione DO description: (pagina 16) Impostazione dei valori di uscite digitali. Cliccando sul riquadro DO dal manù di configurazione si apre la pagina di settaggio che elenca le possibili uscite digitali da configurare. La pagina presa come esempio mostra le prime 14 DO (da 0 a 13), ma ciò che sarà detto per questa pagina vale anche per la pagina “DO 14-19”. Per configurare la DO_0 premere sul tasto CFG a lato di essa.

id: Figura 13. Utenza/funzione DO description: (pagina 16) Impostazione dei valori di uscite digitali. Cliccando sul riquadro DO dal manù di configurazione si apre la pagina di settaggio che elenca le possibili uscite digitali da configurare. La pagina presa come esempio mostra le prime 14 DO (da 0 a 13), ma ciò che sarà detto per questa pagina vale anche per la pagina “DO 14-19”. Per configurare la DO_0 premere sul tasto CFG a lato di essa.

id: Figura 14. Scelta della DO e applicazione della configurazione description: (pagina 17) Una volta scelta la combinazione di utenza/funzione comparirà nella barra a sinistra un tasto di salva ed esci per applicare la configurazione scelta. Quanto detto è rappresentato nella figura che segue.

id: Figura 15. Configurazione AI description: (pagina 18) Impostazione di ingressi analogici. La pagina presa come esempio mostra le prime 6 AI (da 0 a 5), ma ciò che sarà detto per questa pagina vale anche per le seguenti “AI 6-11”, “AI 12-17”, “AI 18-19”.
Per uscire dalla pagina e tornare alla pagina di configurazione, premere sulla freccia in basso a destra. Il valore grezzo vicino alla scritta AI_XX indica lo stato attuale del segnale 4-20 mA. Sarà di seguito mostrata la configurazione della AI_0, ma quanto detto per essa, vale per le altre.

id: Figura 16. Scelta dell’ingresso analogico description: (pagina 18) Impostazione di ingressi analogici. La pagina presa come esempio mostra le prime 6 AI (da 0 a 5), ma ciò che sarà detto per questa pagina vale anche per le seguenti “AI 6-11”, “AI 12-17”, “AI 18-19”.
Per uscire dalla pagina e tornare alla pagina di configurazione, premere sulla freccia in basso a destra. Il valore grezzo vicino alla scritta AI_XX indica lo stato attuale del segnale 4-20 mA. Sarà di seguito mostrata la configurazione della AI_0, ma quanto detto per essa, vale per le altre. Con la stessa filosofia di configurazione, cliccando su CFG si può configurare l’ingresso analogico.

id: Figura 17. Ingresso analogico configurato description: (pagina 19) Ingresso analogico configurato

id: Figura 18. Configurazione AO description: (pagina 20) Sarà di seguito mostrata la configurazione della AO_0, ma quanto detto per essa, vale per le altre. Da questa pagina è possibile effettuare la configurazione delle analogiche in uscita cliccando su CFG.

id: Figura 19. Scelta dei riferimenti description: (pagina 20) Scelta dei riferimenti

id: Figura 20. Gestione Pompe – pag 1 description: (pagina 22) È la parte di configurazione relativa alla gestione delle pompe installate. Cliccando sull’apposito riquadro si enra nel menù di configurazione. La sessione dedicata alle pompe si compone di 4 pagine di configurazione accessibili dalla barra di navigazione inferiore.

id: Figura 21. Gestione Pompe – pag 2 description: (pagina 23) È la parte di configurazione relativa alla gestione delle pompe installate. Cliccando sull’apposito riquadro si enra nel menù di configurazione. La sessione dedicata alle pompe si compone di 4 pagine di configurazione accessibili dalla barra di navigazione inferiore.

id: Figura 22. Gestione Pompe – pag 3 description: (pagina 24) È la parte di configurazione relativa alla gestione delle pompe installate. Cliccando sull’apposito riquadro si enra nel menù di configurazione. La sessione dedicata alle pompe si compone di 4 pagine di configurazione accessibili dalla barra di navigazione inferiore. . Questa è una pagina relativa alle note di intervento. Si possono inserire le informazioni relative alle utenze installate

id: Figura 23. Gestione Pompe – pag 4 description: (pagina 25) È la parte di configurazione relativa alla gestione delle pompe installate. Cliccando sull’apposito riquadro si enra nel menù di configurazione. La sessione dedicata alle pompe si compone di 4 pagine di configurazione accessibili dalla barra di navigazione inferiore.

id: Figura 24. Schematizzazione curve di avviamento motore, protezione termica e magnetica description: (pagina 26) Dal grafico in figura 24, si può osservare come varia la corrente assorbita in funzione del tempo dalla fase di avvio fino a quella di regime. Il controllo dell’assorbimento avviene dopo che la pompa ha superato la fase transitoria.

id: Figura 25. Configurazione Gruppo 1 – pag 1 description: (pagina 27) È la sezione dedicata al settaggio delle logiche di funzionamento del T.T. Control PRO. Le logiche di funzionamento del sistema si gestiscono in gruppi di utenze: si abiliteranno i gruppi di utenze e le logiche verranno applicate al gruppo abilitato. In pratica il sistema gestisce la combinazione di 6 utenze e 2 gruppi ai quali si assegnano le logiche: es. 3 pompe nel gruppo 1 che svuotano una vasca, oppure 2 pompe nel gruppo 2 che riempiono un serbatoio. Vediamo con l’aiuto delle immagini come si configura il sistema. La configurazione sarà descritta per il gruppo 1; tutto ciò descritto per il gruppo 1 vale anche per il gruppo 2.

id: Figura 26. Configurazione Gruppo 1 – pag 2 description: (pagina 28) È la pagina relativa alla logica a galleggianti. Se i galleggianti sono cablati al PLC e configurati nella sezione Digital Input, il T.T. Control PRO-S è in grado di effettuare rotazione delle pompe. Per l’abilitazione della logica di soccorso a galleggianti da software basta semplicemente cliccare sull’apposito selettore switch ON-OFF. Vi sono due scelte disponibili: − Alto per singola pompa – Basso GRP1: si intende una configurazione formata da un galleggiante di basso (GRP1-2 – Logica gall. Basso) che servirà per fermare tutte le pompe in marcia e N galleggianti di alto per quante pompe si vogliono far partire. Con questa configurazione al primo galleggiante (U1 – Logica gall. alto) partirà la prima pompa della sequenza, al secondo (U2 – Logica gall. alto) la seconda pompa e così via. Le pompe poi si fermeranno quando il livello vasca scenderà sotto il galleggiante di basso. In questa situazione il software continuerà la rotazione a tempo o a fermata impostata precedentemente. − Alto GRP1 – Basso GRP1: si intende una configurazione formata da un galleggiante di basso (GRP1-2 – Logica gall. Basso) che servirà per fermare tutte le pompe in marcia e un galleggiante di alto (GRP1-2 – Logica gall. Alto) generale che farà partire le pompe. Con questa configurazione al raggiungimento del galleggiante di alto partirà la prima pompa, passati gli X minuti impostati in “Tempo partenza nuova pompa con galleggiante di alto GRP1” partirà la seconda, e così via. Le pompe si fermeranno quando il livello vasca scenderà sotto il galleggiante di basso. In questa situazione il software continuerà la rotazione a tempo o a fermata impostata precedentemente.

id: Figura 27. Svuotamento Totale Vasca description: (pagina 29) La logica di svuotamento totale vasca consente all’operatore l’abilitazione di un vero e proprio planning di gestione e manutenzione. Con questa operazione si può decidere di svuotare la vasca fino ad un setpoint impostato in determinati giorni della settimana a partire da un determinato orario. Lo svuotamento in corso verrà visualizzato sul sinottico con una scritta in rosso. Nel caso in Figura 27. alle ore 1:00 dei giorni martedì e sabato, in qualsiasi situazione si trovi l’impianto, il software accende tutte le pompe in Remoto ed in Automatico per far sì che il livello di riferimento (Sonda logica 1 o Sonda logica 2) della vasca scenda sotto il valore impostato di 0.8m. Al termine della funzione si ritornerà al normale funzionamento.

id: Figura 28. Configurazione PID – pag 1 description: (pagina 30) Da questa pagina è possibile abilitare e configurare gli inseguimenti PID. Saranno presentate i settaggi per il gruppo 1, ma tutto ciò che sarà detto varrà anche per il gruppo 2. L’inseguimento PID può essere fatto secondo due modalità: monostadio o multistadio. La scelta viene fatta tramite il selettore switch PID MULTISTADIO (in verde = ON, è abilitato il multistadio). − Monostadio: questa funzione implica che l’uscita del PID (e quindi la modulazione in frequenza) venga data in contemporanea a tutte le utenze le quali lavoreranno tutte alla stessa frequenza − Multistadio: questa funzione implica che l’uscita del PID (e quindi la modulazione in frequenza) venga data solo alla prima utenza della sequenza. La logica è la seguente: la prima utenza parte e si ferma per le soglie start/stop impostate. Su tale utenza sarà fatta la modulazione in frequenza. Se essa arriverà alla massima velocità e vi resterà per il tempo X impostato verrà fatta partire la seconda utenza a massima velocità, mentre continuerà la modulazione sulla prima. Nel caso in cui la prima utenza arrivi a minima velocità e vi resti per il tempo X impostato, allora verrà spenta l’ultima utenza avviata a massima frequenza.

id: Figura 29. Configurazione PID – pag 3 description: (pagina 31) Nella pagina 3 delle configurazioni PID è possibile gestire il filtraggio delle sonde e l’abilitazione dei setpoint da inseguire in determinate fasce orarie.
La logica con setpoint a fasce orarie presentata in figura 29 prevede che dalle ore 06:00 alle ore 22:00 il setpoint che inseguirà il PID impostato per il gruppo 1 sarà 3.5, mentre dalle ore 22:01 alle 5:59 il PID inseguirà il valore di 2,9. Il filtraggio delle sonde invece rappresenta la risposta del filtro al valore analogico 4-20mA in ingresso al PLC, più è alto il valore (non minore di 40) più la risposta del filtro sarà lenta.

id: Figura 30. Configurazione Sinottico – Pompe esterne alla vasca e vasca assente description: (pafina 32) In questa pagina si andrà a configurare il sinottico da visualizzare, il nome dell’impianto, il colore della marcia delle utenze, il tempo del reset modem (se presente), il livello di sfioro della vasca (se presente), i tempi di watchdog e di ripristino automatico per le grandezze Sonda logica 1 e Sonda logica 2. Il valore aggiunto del sistema è la completa personalizzazione del sinottico. È possibile avere 3 scenari di funzionamento in funzione delle logiche da implementare: − Utenze esterne alla vasca e vasca assente: tipico di uno scenario ad immissione direttamente in condotta; − Utenze esterne alla vasca e vasca presente: si riferisce ad una logica a riempimento verso un serbatoio; − Utenze interne alla vasca: scenario classico di un sollevamento fognario dove è necessario svuotare una vasca di raccolta. La personalizzazione del sinottico è facilmente impostabile dai selettori messi a disposizione nella relativa pagina (come mostrato in figura 28).

id: Figura 31. Configurazione Sinottico – Pompe esterne alla vasca e vasca presente description: (pagina 33) In Figura 31 e 32, sono rappresentati gli altri due scenari possibili di funzionamento. È utile per l’operatore visualizzare in anteprima in basso alla pagina il layout che sta configurando.

id: Figura 32. Configurazione Sinottico – Pompe interne alla vasca description: (pagina 34) In Figura 31 e 32, sono rappresentati gli altri due scenari possibili di funzionamento. È utile per l’operatore visualizzare in anteprima in basso alla pagina il layout che sta configurando.

id: Figura 34. Configurazione Sinottico – pag 3 description: In questa pagina è possibile cambiare il nome dei consensi esterni impostati e delle sonde abilitate al funzionamento del sistema. In questa pagina è possibile cambiare il nome delle segnalazioni disponibili se configurate negli ingressi digitali. Dalla stessa pagina è possibile resettare ad impostazioni di fabbrica il T.T. Control PRO-S. Prima di procedere l’operatore sarà avvistaso da un pop-up di conferma come in figura 35.

id: Figura 35. Reset TT Control PRO description: (pagina 35) Dalla stessa pagina è possibile resettare ad impostazioni di fabbrica il T.T. Control PRO-S. Prima di procedere l’operatore sarà avvistaso da un pop-up di conferma come in figura seguente.

id: Figura 36. Abilitazione Trends description: (pagina 36) Nella pagina dei trends è possibile abilitare i trends per le sonde analogiche che sono cablate al PLC. Mettendo nello stato di ON il relativo segnale analogico si inizierà a conservare i valori di quella grandezza nel tempo. Successivamente vedremo come consultare i trends. Per le sonde dal campo sarà mostrato il nome inserito nella pagina configurazione sinottico -2 (vedi pag. 34).

id: Figura 37. Export Dati description: (pagina 37) Da questa pagina sarà possibile effettuare l’esportazione dei dati storici su chiavetta USB. È necessario inserire le seguenti informazioni prima di procedere all’esportazione: − Report Title: identificativo dell’esportazione; − Start Date: è la data di inizio esportazione. È necessario mantenere la formattazione “YYYY MM-DD HH:NN:SS” comprensivo di caratteri speciali, ad esempio “2019-05-28 12:15:00”; − End Date: è la data di inizio esportazione. È necessario mantenere la formattazione “YYYY MM-DD HH:NN:SS” comprensivo di caratteri speciali, ad esempio “2019-05-28 16:27:00”; Una volta completato l’inserimento dei valori, fare click sul tasto “Salva report sonde” se si vuole fare l’export delle sonde analogiche collegate al sistema, mentre fare click sul tasto “Salva report pompe” se si vuole fare l’export delle sonde analogiche collegate alle utenze. Il file generato sarà di formato.txt e salvato nella cartella principale del disco USB inserito.

id: Figura 38. Gestione Utenti - 1 description: (pagina 38) Cliccando su gestione utenti si aprirà la popup per la configurazione dei gruppi utenti. Da qui è possibile creare un nuovo gruppo utenti assegnandoci poi un nome e un livello. A questo gruppo cliccando su nuovo utente è possibile assegnare più utenti. Al nuovo utente è possibile assegnare il nome (che sarà poi l’user) una password e un livello utente. Creati i gruppi e gli utenti cliccando su Ok il sistema accetterà le modifiche. Per utilizzare l’applicazione è necessario essere loggati con l’adeguato livello. I livelli che hanno i permessi per utilizzare l’applicazione sono: Livello 8 o superiore: utilizzo completo dell’applicazione Livello 7: utilizzo dell’applicazione soltanto per la gestione dell’impianto. E’ possibile comandare le utenze, ma non è possibile configurare l’applicazione. Quindi nella configurazione di un nuovo utente ha senso inserire livelli di tipo 7 o superiore.

id: Figura 40. Gestione Data e Ora description: (pagina 40) In questa pagina si andrà a configurare la data e l’ora del sistema. Per effettuare il cambio data e/o ora è necessario seguire i seguenti steps: - - scrivere nella casella INSERT il nuovo valore da cambiare, esempio 2020 nella casella set anno; premere su SET ed attendere che il dato sarà letto nella relativa casella READ; a quel punto il dato cambiato.

**richiesta**:

Dovrai generare molteplici workinstructions relative al documento fornito in input e presente nel vector store. inoltre fai riferimento all indice (se presente) per comprendere come muoverti tra i contenuti ed effettua chiamate per approfondire il dettalgio dei contenuti letti. Duqnue crea tutte le workflows che reputi opportuni, uno per ogni sottoprocedura individuata nel documento. Oltre ai riferimenti alle apgine del documento, all interno dei task inserisci anche riferimenti alle immagini citate nel seguente contenuto, il quale mostra le immagini del docuemntoa ssociate ad un id e ad un campo fescrizione che contiene una descrizione sitentitca oppure un frammento di contesto relativo all immagine. devi creare workflows basati sulle procedure interne msotrate ne docuemtno, duqnue le varie procedure di setup e configurazioni mostrate relative al contenuto del docuemnto


**output**:

Per creare i workflow dettagliati relativi alle procedure di setup e configurazione del software T.T. Control PRO, seguirò l'indice del documento e utilizzerò le descrizioni delle immagini fornite. Procederò a creare i workflow per le seguenti sezioni:

    Configurazione del T.T. Control PRO
        Mappa delle Pagine di Configurazione
        Ingressi Digitali - DI
        Uscite Digitali - DO
        Ingressi Analogici - AI
        Uscite Analogiche - AO
        Configurazione Pompe
        Configurazione Logiche Gruppi
        Configurazione PID
        Configurazione Sinottico
        Abilitazione Trends
        Esportazione su USB
        Gestione Utenti
        Configurazione Data e Ora

Inizierò con la sezione "Configurazione del T.T. Control PRO". Per ottenere informazioni dettagliate, effettuerò una ricerca nel vector store.Ho ottenuto informazioni dettagliate sulla sezione "Configurazione del T.T. Control PRO" dal vector store. Procederò ora a creare i workflow per le sottosezioni di configurazione, includendo riferimenti alle pagine del documento e alle immagini pertinenti. Inizierò con la "Mappa delle Pagine di Configurazione" e proseguirò con le altre sottosezioni.

Workflow 1: Mappa delle Pagine di Configurazione

{
  "workflow": [
    {
      "id": "task1",
      "name": "Accesso al Menù di Configurazione",
      "description": "Accedere al menù di configurazione principale del T.T. Control PRO.",
      "type": "userTask",
      "assignee": "Operatore",
      "candidateGroups": ["Tecnici"],
      "formKey": "configurationMenuAccessForm",
      "genericFields": {},
      "mediaContent": {
        "documents": [
          {
            "id": "file1",
            "name": "Manuale d'uso per l'operatore (pagina 12)",
            "description": "Descrizione delle icone del menù di configurazione."
          }
        ],
        "images": [
          {
            "id": "Figura 7",
            "name": "Menù di configurazione principale",
            "description": "Menù di configurazione principale del T.T. Control PRO."
          }
        ]
      },
      "script": null,
      "conditions": [],
      "variables": {}
    }
  ]
}

Workflow 2: Configurazione Ingressi Digitali (DI)

{
  "workflow": [
    {
      "id": "task2",
      "name": "Configurazione Ingressi Digitali",
      "description": "Impostare i valori di ingressi digitali nel sistema T.T. Control PRO.",
      "type": "userTask",
      "assignee": "Operatore",
      "candidateGroups": ["Tecnici"],
      "formKey": "digitalInputConfigurationForm",
      "genericFields": {},
      "mediaContent": {
        "documents": [
          {
            "id": "file1",
            "name": "Manuale d'uso per l'operatore (pagina 13)",
            "description": "Impostazione dei valori di ingressi digitali."
          }
        ],
        "images": [
          {
            "id": "Figura 8",
            "name": "Configurazione DI",
            "description": "Impostazione dei valori di ingressi digitali."
          },
          {
            "id": "Figura 9",
            "name": "Scelta funzioni/gruppi/utenze DI",
            "description": "Configurazione delle funzioni per ogni utenza e gruppo."
          }
        ]
      },
      "script": null,
      "conditions": [],
      "variables": {}
    }
  ]
}

Workflow 3: Configurazione Ingressi Digitali (DI)

{
  "workflow": [
    {
      "id": "task1",
      "name": "Accesso alla Configurazione degli Ingressi Digitali",
      "description": "Accedere alla pagina di configurazione degli ingressi digitali (DI) dal menù principale. Toccare il riquadro 'DI' per aprire la pagina di configurazione. Qui verranno elencati i possibili ingressi digitali da configurare.",
      "type": "userTask",
      "assignee": "Operatore",
      "candidateGroups": ["Tecnici"],
      "formKey": "digitalInputAccessForm",
      "genericFields": {},
      "mediaContent": {
        "documents": [
          {
            "id": "file1",
            "name": "Manuale d'uso per l'operatore (pagina 13)",
            "description": "Impostazione dei valori di ingressi digitali."
          }
        ],
        "images": [
          {
            "id": "Figura 8",
            "name": "Configurazione DI",
            "description": "Impostazione dei valori di ingressi digitali."
          }
        ]
      },
      "script": null,
      "conditions": [],
      "variables": {}
    },
    {
      "id": "task2",
      "name": "Configurazione di un Ingresso Digitale",
      "description": "Selezionare un ingresso digitale da configurare, ad esempio DI_0. Premere sul tasto 'CFG' a lato dell'ingresso per accedere alle opzioni di configurazione. Assegnare le funzioni desiderate per l'utenza, il gruppo, e altre segnalazioni. Impostare i contatti come NC (Normalmente Chiuso) o NO (Normalmente Aperto).",
      "type": "userTask",
      "assignee": "Operatore",
      "candidateGroups": ["Tecnici"],
      "formKey": "digitalInputConfigurationForm",
      "genericFields": {},
      "mediaContent": {
        "documents": [
          {
            "id": "file1",
            "name": "Manuale d'uso per l'operatore (pagina 14)",
            "description": "Dettagli sulla configurazione degli ingressi digitali."
          }
        ],
        "images": [
          {
            "id": "Figura 9",
            "name": "Scelta funzioni/gruppi/utenze DI",
            "description": "Configurazione delle funzioni per ogni utenza e gruppo."
          }
        ]
      },
      "script": null,
      "conditions": [],
      "variables": {}
    },
    {
      "id": "task3",
      "name": "Salvataggio della Configurazione",
      "description": "Dopo aver configurato l'ingresso digitale, controllare la configurazione per evitare duplicati o errori. Se il controllo è positivo, applicare la configurazione premendo il tasto 'Salva e Esci'.",
      "type": "userTask",
      "assignee": "Operatore",
      "candidateGroups": ["Tecnici"],
      "formKey": "saveConfigurationForm",
      "genericFields": {},
      "mediaContent": {
        "documents": [
          {
            "id": "file1",
            "name": "Manuale d'uso per l'operatore (pagina 15)",
            "description": "Procedura di salvataggio della configurazione."
          }
        ],
        "images": [
          {
            "id": "Figura 10",
            "name": "Controllo Configurazione e Salvataggio",
            "description": "Verifica e salvataggio della configurazione."
          }
        ]
      },
      "script": null,
      "conditions": [],
      "variables": {}
    }
  ]
}
"""