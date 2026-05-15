


from pydantic import BaseModel


class CompleteTaskRequest(BaseModel):
    actual_minutes : int
    difficulty : str
    comment : str = None
    task_id : int