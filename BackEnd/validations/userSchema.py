from pydantic import BaseModel
from datetime import date


class EmailRequest(BaseModel):
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