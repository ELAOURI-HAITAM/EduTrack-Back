


from pydantic import BaseModel


class TaskRequest(BaseModel):
    title : str
    actual_minutes : int
    difficulty : str
    comment : str = None
    resource_id : int