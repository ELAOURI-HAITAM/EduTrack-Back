from typing import Optional
from pydantic import BaseModel
from datetime import date


class createUserRequest(BaseModel):
    email : str
    role : str

class EmailRequest(BaseModel) : 
    email : str


class VerifyOTPRequest(BaseModel):
    email : str
    otp : str
    
    
    
class CompleteStudentProfileRequest(BaseModel):
    password : str
    first_name : str
    last_name : str
    birth_date : date
    gender : str
    
class CompleteProfessorProfileRequest(BaseModel):
    password : str
    first_name : str
    last_name : str
    birth_date : date
    gender : str
    phone_number : str
    
    
class LoginRequest(BaseModel) :
    email  : str
    password : str


class ChangePasswordRequest(BaseModel) :
    new_password : str
    confirm_password : str


class UpdateUserInfosRequest(BaseModel) : 
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    role : Optional[str] = None
    birth_date: Optional[date] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None 