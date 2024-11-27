from fastapi import FastAPI, HTTPException
from models import WorkflowInput, WorkflowOutput, UserTask, GenericField, Condition
# from agent import generate_workflow  # Da implementare

app = FastAPI(
    title="Workflow Generator API",
    description="""
API per la generazione automatizzata di workflow basati su input complessi, tra cui documenti, media e istruzioni fornite dall'utente. L'API utilizza un agente LLM per analizzare i dati di input e creare un workflow strutturato compatibile con Camunda.
""",
    version="1.0.0"
)

# Placeholder per la funzione di connessione all'agente
def generate_workflow(input_data: WorkflowInput) -> WorkflowOutput:
    # Questa funzione dovrebbe connettersi all'agente LLM per generare il workflow
    # Attualmente ritorna un output simulato con un task di esempio
    # Da implementare

    example_task = UserTask(
        id="task_1",
        name="Assemblare la Base",
        description="L'utente deve assemblare la base del mobile seguendo le istruzioni.",
        type="userTask",
        assignee="user_123",
        candidateGroups=["assemblers"],
        formKey="assembly_form",
        mediaContent=input_data.media,
        conditions=[
            Condition(
                conditionExpression="${assemblyComplete == true}",
                nextTaskId="task_2"
            )
        ],
        variables={
            "assemblyComplete": GenericField(type="Boolean", value=False)
        }
    )

    return WorkflowOutput(tasks=[example_task])

@app.post("/generate-workflow", response_model=WorkflowOutput, summary="Genera un workflow basato sull'input fornito", tags=["Workflow"])
async def generate_workflow_endpoint(input_data: WorkflowInput):
    """
    Genera un workflow strutturato basato sul `README` e sui media forniti.

    - **readme**: Contiene le istruzioni generali e l'obiettivo del workflow.
    - **media**: Raccolta di documenti, immagini e video associati.

    L'endpoint ritorna una lista di task che compongono il workflow.
    """
    try:
        # Logica per gestire l'input e chiamare l'agente
        workflow_output = generate_workflow(input_data)
        return workflow_output
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8100)
