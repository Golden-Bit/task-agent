import requests
import base64
import json
import os


def test_generate_workflows_from_local_files():
    # URL dell'endpoint da testare
    url = 'http://127.0.0.1:8091/generate_workflows'

    # Percorsi dei file locali da caricare
    local_files = [
        {'path': 'certificato.pdf', 'description': 'Descrizione del file 1'},
        #{'path': 'file2.txt', 'description': 'Descrizione del file 2'}
    ]

    # Lista per contenere i dati dei file codificati
    files_data = []

    # Leggi e codifica i file in Base64
    for file_info in local_files:
        file_path = file_info['path']
        description = file_info['description']
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                content_base64 = base64.b64encode(f.read()).decode('utf-8')
                files_data.append({
                    'id_file': os.path.basename(file_path),  # Usa il nome del file come ID
                    'content_base64': content_base64,
                    'description': description
                })
        else:
            print(f"File non trovato: {file_path}")

    # Crea i dati di input secondo il modello GenerateWorkflowsInput
    input_data = {
        'files': files_data,
        'prompt': 'Inserisci qui le direttive e linee guida fornite dall\'utente.'
    }

    # Imposta l'header Content-Type
    headers = {'Content-Type': 'application/json'}

    # Invia la richiesta POST all'endpoint
    try:
        response = requests.post(url, headers=headers, data=json.dumps(input_data))

        # Gestisce la risposta
        if response.status_code == 200:
            print('Richiesta completata con successo.')
            print('Risposta:', response.json())
        else:
            print(f'Errore nella richiesta: {response.status_code}')
            print('Dettagli:', response.text)
    except Exception as e:
        print(f'È occorso un errore durante la richiesta: {e}')


if __name__ == '__main__':
    test_generate_workflows_from_local_files()
