import requests
import base64
import json
import os

def test_upload_files_and_generate_workflows():
    """
    Esegue un test end-to-end:
      1) Caricamento (upload) di uno o più file su /upload_files_for_workflow
      2) Generazione di workflow su /generate_workflow
    """
    # -----------------------------------------------------
    # 1) PREPARAZIONE DATI E CONFIGURAZIONE
    # -----------------------------------------------------
    # URL dei due endpoint
    upload_url = 'http://127.0.0.1:8091/upload_files_for_workflow'
    generate_url = 'http://127.0.0.1:8091/generate_workflow'

    # session_id scelto dall'utente (puoi generarlo anche dinamicamente)
    session_id = 'test_session_002'

    # Percorsi dei file locali da caricare
    local_files = [
        {'path': 'certificato.pdf', 'description': 'Descrizione del certificato'}
        # Aggiungi altri file qui, se necessario
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

    # -----------------------------------------------------
    # 2) CHIAMATA ALL'ENDPOINT DI UPLOAD
    # -----------------------------------------------------
    # Input secondo il modello UploadWorkflowFilesInput
    upload_input_data = {
        'session_id': session_id,
        'files': files_data
    }

    # Invio la richiesta POST di upload
    try:
        response_upload = requests.post(
            upload_url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(upload_input_data)
        )
        if response_upload.status_code in [200, 202]:
            print('Upload completato con successo!')
            print('Risposta Upload:', response_upload.json())
        else:
            print(f'Errore nella richiesta di upload: {response_upload.status_code}')
            print('Dettagli:', response_upload.text)
            return  # Interrompe il test in caso di fallimento
    except Exception as e:
        print(f'È occorso un errore durante la richiesta di upload: {e}')
        return

    #if True:
    #    return

    # -----------------------------------------------------
    # 3) CHIAMATA ALL'ENDPOINT DI GENERAZIONE WORKFLOW
    # -----------------------------------------------------
    # Input secondo il modello GenerateWorkflowInput
    # Prompt di esempio (puoi personalizzarlo a piacere)
    prompt_text = "Analizza i file caricati e genera workflow di configurazione."

    generate_input_data = {
        'session_id': session_id,
        'prompt': prompt_text,
        'max_iterations': 2  # Esempio di valore
    }

    try:
        response_generate = requests.post(
            generate_url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(generate_input_data)
        )
        if response_generate.status_code in [200, 202]:
            print('Generazione workflow completata con successo!')
            print('Risposta Workflow:', response_generate.json())
        else:
            print(f'Errore nella richiesta di generazione workflow: {response_generate.status_code}')
            print('Dettagli:', response_generate.text)
    except Exception as e:
        print(f'È occorso un errore durante la richiesta di generazione workflow: {e}')


if __name__ == '__main__':
    test_upload_files_and_generate_workflows()
