from typing import Any
import requests
import json


def upload_media_files(payload: Any, callback_url: str = "https://dev-aigo.theia-innovation.com/api/v1"):
    url = f"{callback_url}/instructions/media"

    # Headers: imposta Content-Type e, se richiesto, il token di autorizzazione
    #headers = {
    #    "Content-Type": "application/json",
    #    "Authorization": "Bearer <LA_TUA_AUTH_TOKEN>"  # Rimuovi o modifica se non serve
    #}

    # Invia la richiesta POST con il payload in JSON
    response = requests.post(url,
                             #headers=headers,
                             data=json.dumps(payload))

    # Verifica la risposta
    if response.status_code == 200 or response.status_code == 201:
        print("Caricamento avvenuto con successo:", response.json())
    else:
        print(f"Errore durante il caricamento. Codice HTTP: {response.status_code}")
        print("Dettagli:", response.text)


def send_workflows(payload: Any, callback_url: str = "https://dev-aigo.theia-innovation.com/api/v1"):
    url = f"{callback_url}/instructions/webhook"

    # Esempio di headers: aggiungi token se necessario
    #headers = {
    #    "Content-Type": "application/json",
    #    "Authorization": "Bearer <IL_TUO_TOKEN_SE_SERVE>"
    #}

    try:
        response = requests.post(
            url,
            # headers=headers,
            data=json.dumps(payload),
            #timeout=30  # puoi regolare il timeout
        )

        if response.status_code in [200, 201]:
            print("Workflows inviati con successo!")
            print("Risposta:", response.json())
        else:
            print(f"Errore nell'invio. Codice HTTP: {response.status_code}")
            print("Dettagli:", response.text)

    except requests.exceptions.RequestException as e:
        print("Si è verificato un errore di connessione o timeout:", e)


if __name__ == "__main__":

    # Esempio di payload (array di media objects), in linea con lo schema mostrato nello Swagger
    payload_1 = [
        {
            "session_id": "abc123-123-abc",
            "file_id": "abc123-123-abc",
            "file_type": "pdf",
            "source_file": "source_file_001",
            "title": "Sample File",
            "description": "This is a test file",
            "b64_content": "SGVsbG8gd29ybGQ="
        }
        # Puoi aggiungere ulteriori file (dizionari) nell'array se necessario
    ]

    # Esempio di payload, basato sullo schema pubblicato nello Swagger.
    payload_2 = {
        "session_id": "abc123-123-abc",
        "workflows": [
            {
                "id": "workflow_001",
                "title": "Esempio Workflow",
                "description": "Un workflow di esempio per illustrare la struttura richiesta.",
                "media": [
                    {
                        "file_id": "file_pdf",
                        "file_type": "pdf",
                        "source_file": "src_pdf_file",
                        "title": "Manuale PDF",
                        "description": "Manuale in formato PDF"
                    }
                ],
                "workflow": [
                    {
                        "id": "task1",
                        "name": "Task di esempio",
                        "description": "Eseguire la configurazione iniziale del sistema.",
                        "type": "userTask",
                        "assignee": "Tecnico1",
                        "candidateGroups": ["GruppoTecnici"],
                        "formKey": "configForm",
                        "genericFields": {},
                        "mediaContent": {
                            "documents": [
                                {
                                    "file_id": "file_pdf",
                                    "file_type": "pdf",
                                    "source_file": "src_pdf_file",
                                    "title": "Manuale PDF",
                                    "description": "Dettagli per la configurazione."
                                }
                            ],
                            "images": [
                                {
                                    "file_id": "img001",
                                    "file_type": "jpg",
                                    "source_file": "src_pdf_file",
                                    "title": "Schermata di Configurazione",
                                    "description": "Anteprima della pagina di configurazione."
                                }
                            ],
                            "videos": []
                        },
                        "script": "echo 'Esempio di script o istruzione';",
                        "conditions": [
                            "task1.completed"
                        ],
                        "variables": {}
                    }
                ]
            }
        ]
    }

    upload_media_files(payload_1)
    print("\n\n" + "---"*25 + "\n\n")
    send_workflows(payload_2)

