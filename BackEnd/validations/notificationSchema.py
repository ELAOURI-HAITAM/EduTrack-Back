

from typing import Literal
from pydantic import BaseModel


class BroadCastNotification(BaseModel) : 
    title : str
    message : str
    target : Literal["All" , "Student" , "Professor"] = "All"