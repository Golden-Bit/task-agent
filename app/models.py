from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

# Modelli per i media
class MediaBase(BaseModel):
    id: str = Field(..., description="Identificatore univoco del media", example="img1")
    name: str = Field(..., description="Nome descrittivo del media", example="Diagramma dei Componenti")
    description: str = Field(..., description="Descrizione del contenuto o dello scopo del media", example="Illustrazione dei componenti del mobile.")
    type: str = Field(..., description="Formato del media (ad esempio, 'base64')", example="base64")
    value: str = Field(..., description="Contenuto del media codificato in Base64", example="base64_encoded_content")

class Document(MediaBase):
    pass

class Image(MediaBase):
    pass

class Video(MediaBase):
    pass

class MediaContent(BaseModel):
    documents: List[Document] = Field(default_factory=list, description="Lista di documenti associati al task")
    images: List[Image] = Field(default_factory=list, description="Lista di immagini associate al task")
    videos: List[Video] = Field(default_factory=list, description="Lista di video associati al task")

# Modello di input
class WorkflowInput(BaseModel):
    readme: str = Field(..., description="Contiene le istruzioni generali e l'obiettivo del workflow", example="Questo workflow guida l'utente attraverso il montaggio di un mobile...")
    media: MediaContent = Field(..., description="Raccolta di media correlati al workflow")

# Modelli per i task
class GenericField(BaseModel):
    type: str = Field(..., description="Tipo del campo generico", example="string")
    value: Any = Field(..., description="Valore del campo generico", example="Qualsiasi valore")

class Script(BaseModel):
    language: str = Field(..., description="Linguaggio dello script", example="python")
    code: str = Field(..., description="Codice dello script", example="print('Hello World')")

class Condition(BaseModel):
    conditionExpression: str = Field(..., description="Espressione condizionale per il flusso", example="${approved == true}")
    nextTaskId: str = Field(..., description="ID del task successivo se la condizione è soddisfatta", example="task_2")

class TaskBase(BaseModel):
    id: str = Field(..., description="Identificatore univoco del task", example="task_1")
    name: str = Field(..., description="Nome descrittivo del task", example="Assemblare la Base")
    description: str = Field(..., description="Descrizione dettagliata delle attività richieste per il task", example="L'utente deve assemblare la base del mobile seguendo le istruzioni.")
    type: str = Field(..., description="Tipo di task (es. 'userTask', 'serviceTask', 'externalTask')", example="userTask")
    genericFields: Optional[Dict[str, GenericField]] = Field(default_factory=dict, description="Campi generici per informazioni addizionali")
    mediaContent: Optional[MediaContent] = Field(default=None, description="Media associati al task")
    script: Optional[Script] = Field(default=None, description="Script da eseguire nel task")
    conditions: Optional[List[Condition]] = Field(default_factory=list, description="Condizioni per determinare i flussi successivi")
    variables: Optional[Dict[str, GenericField]] = Field(default_factory=dict, description="Variabili di processo utilizzabili durante l'esecuzione del task")

# Task specifici
class UserTask(TaskBase):
    assignee: Optional[str] = Field(default=None, description="Utente assegnato al task", example="user_123")
    candidateGroups: Optional[List[str]] = Field(default_factory=list, description="Gruppi candidati per l'assegnazione del task", example=["assemblers"])
    formKey: Optional[str] = Field(default=None, description="Chiave del form associato al task", example="assembly_form")

class ServiceTask(TaskBase):
    implementation: Optional[str] = Field(default=None, description="Implementazione del task di servizio", example="myServiceTaskImplementation")
    delegateExpression: Optional[str] = Field(default=None, description="Espressione del delegato per il task", example="${delegateExpression}")
    resultVariable: Optional[str] = Field(default=None, description="Nome della variabile dove salvare il risultato", example="serviceResult")

class ExternalTask(TaskBase):
    topicName: str = Field(..., description="Nome del topic per l'External Task", example="inventoryUpdate")
    workerId: Optional[str] = Field(default=None, description="ID del worker che esegue il task", example="worker_456")
    lockExpirationTime: Optional[str] = Field(default=None, description="Tempo di scadenza del lock in formato ISO 8601", example="2023-10-31T12:00:00Z")
    priority: Optional[int] = Field(default=0, description="Priorità del task", example=10)
    retries: Optional[int] = Field(default=3, description="Numero di tentativi in caso di errore", example=5)
    errorMessage: Optional[str] = Field(default=None, description="Messaggio di errore in caso di fallimento", example="Errore nel processamento dell'External Task")
    errorDetails: Optional[str] = Field(default=None, description="Dettagli aggiuntivi sull'errore", example="Stack trace o informazioni addizionali")

# Unione dei task
Task = Union[UserTask, ServiceTask, ExternalTask]

# Modello di output
class WorkflowOutput(BaseModel):
    tasks: List[Task] = Field(..., description="Lista dei task generati nel workflow")
