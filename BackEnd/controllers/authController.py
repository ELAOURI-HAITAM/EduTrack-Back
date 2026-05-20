from datetime import datetime, timedelta
import email
import random
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi_mail import MessageSchema, MessageType
from sqlalchemy.orm import Session
from models.professor import Professor
from database.connexion import get_db
from mail.mailer import fm
from middleware.auth import get_current_user
from middleware.token import access_token
from models.student import Student
from models.user import User, UserRole
from validations.userSchema import (
    ChangePasswordRequest,
    CompleteProfessorProfileRequest,
    CompleteStudentProfileRequest,
    EmailRequest,
    LoginRequest,
    VerifyOTPRequest,
)
from utils.hash import get_password_hash, verify_password

auth_router = APIRouter(prefix="/users")


# @auth_router.post("/add")
# def store(request: EmailRequest, db: Session = Depends(get_db)):

#     domain = request.email.split("@")[-1]

#     allowed_domains = [
#     "prof.edu.ac.ma",
#     "student.edu.ac.ma",
#     ]   

#     if domain not in allowed_domains:
#         raise HTTPException(
#         status_code=400,
#         detail="Invalid email domain"
#     )

#     user = db.query(User).filter(User.email == request.email).first()

#     if user:
#         raise HTTPException(
#             status_code=400,
#             detail="Email already exists"
#         )

#     if domain == "prof.edu.ac.ma":
#         role = "Professor"

#     elif domain == "prof.edu.ac.ma":
#         role = "Student"
    


#     new_user = User(
#         email = request.email,
#         role = role
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     return {
#         "message": "User added successfully",
#         "role": role
#     }


@auth_router.post("/send-otp")
async def send_otp(request: EmailRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email Not Found ")
    if user.password : 
        raise HTTPException(status_code=404, detail="You Already Have An Account ")

    otp_code = str(random.randint(100000, 999999))
    user.otp = otp_code
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=5)
    db.commit()

    message = MessageSchema(
        subject="Your Code",
        recipients=[request.email],
        template_body={"otp": otp_code},
        subtype=MessageType.html,
    )
    await fm.send_message(message, template_name="otp.html")

    return {"message": "we sent code into your account "}


@auth_router.post("/verify-otp")
def verify(request: VerifyOTPRequest,response : Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="email not found")

    if not user.otp_expires_at or user.otp_expires_at < datetime.utcnow():
        raise HTTPException(status_code=404, detail="Code expired")

    if user.password : 
        raise HTTPException(status_code=404, detail="You Alreafy Have An Account")
    if user.otp != request.otp:
        raise HTTPException(status_code=400, detail="Invalide Code")

    user.otp = None
    user.otp_expires_at = None
    db.commit()

    token = access_token(
        {"id": user.id, "email": user.email, "role": user.role.value}
    )
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=3600,
        samesite="lax",
        secure=False,
        path="/"
    )
    return {"access_token": token, "token_type": "bearer" , "message": "code verified successfully ","role": user.role.value}


@auth_router.post("/complete-profile")
def complete_profile(
    request: Union[CompleteStudentProfileRequest, CompleteProfessorProfileRequest],
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    print(f"--- DEBUG ---")
    print(f"Password Received: {request.password}")
    print(f"Length: {len(request.password)}")
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found ")

    user.password = get_password_hash(request.password)

    if user.role.value == "Student":
        new_student = Student(
            first_name=request.first_name,
            last_name=request.last_name,
            gender=request.gender,
            birth_date=request.birth_date,
            user_id=user.id,
        )
        db.add(new_student)
        db.commit()
        return {
            "message": "Profile Completed Successfully ",
            "student_data": new_student,
        }

    elif user.role.value == "Professor":
        new_prof = Professor(
            first_name=request.first_name,
            last_name=request.last_name,
            gender=request.gender,
            birth_date=request.birth_date,
            phone_number=request.phone_number,
            user_id=user.id,
        )
        db.add(new_prof)
        db.commit()
        return {
            "message": "Profile Completed Successfully ",
            "professor_data": new_prof,
        }

    else:
        raise HTTPException(status_code=400, detail="Invalid user role")

@auth_router.post("/login")
def login(request: LoginRequest,response : Response ,db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="email not found ")

    if not user.password:
        raise HTTPException(
            status_code=400,
            detail="Password not set. Complete profile first.",
        )

    password = verify_password(request.password, user.password)
    if not password:
        raise HTTPException(status_code=400, detail="Password Incorrect ")
    if user.role.value == "Student" :
        token = access_token(
        {
            "id": user.id,
            "email": user.email,
            "role": user.role.value,
            "first_name": user.student_data.first_name,
            "last_name": user.student_data.last_name,
            "gender": user.student_data.gender.value,
            "birth_date" : user.student_data.birth_date.isoformat()
        }
    )
    elif(user.role.value == "Professor") :
        token = access_token(
        {
            "id": user.id,
            "email": user.email,
            "role": user.role.value,
            "first_name": user.prof_data.first_name,
            "last_name": user.prof_data.last_name,
            "gender": user.prof_data.gender.value,
            "birth_date" : user.prof_data.birth_date.isoformat(),
            "phone_number" : user.prof_data.phone_number
        }
    
    )
    elif user.role.value == "Admin":
       
        token = access_token({
            "id": user.id,
            "email": user.email,
            "role": user.role.value,
            "first_name": "Admin",     
            "last_name": "System"
        })
    else:
        raise HTTPException(status_code=400, detail="Invalid User Role")
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=3600,
        samesite="lax",
        secure=False,
    )
    return {"message": "Login Successfully ", "token": token , "role" : user.role.value}

@auth_router.post("/logout") 
def logout(response : Response , current_user: User = Depends(get_current_user)) :
    response.delete_cookie(key="access_token")
    return {"message" : "logout Successfully "}



@auth_router.get("/me")
def get_me(current_user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.role.value == "Student":    
        return {
            "id": user.id,
            "email": user.email,
            "role": user.role.value,
            "first_name": user.student_data.first_name if user.student_data else "",
            "last_name": user.student_data.last_name if user.student_data else "",
            "gender": user.student_data.gender.value if user.student_data and user.student_data.gender else "",
            "birth_date": user.student_data.birth_date.isoformat() if user.student_data and user.student_data.birth_date else None
        }
        
    elif user.role.value == "Professor": 
        return {
            "id": user.id,
            "email": user.email,
            "role": user.role.value,
            "first_name": user.prof_data.first_name if user.prof_data else "",
            "last_name": user.prof_data.last_name if user.prof_data else "",
            "gender": user.prof_data.gender.value if user.prof_data and user.prof_data.gender else "",
            "birth_date": user.prof_data.birth_date.isoformat() if user.prof_data and user.prof_data.birth_date else None,
            "phone_number": user.prof_data.phone_number if user.prof_data else ""
        }

    elif user.role.value == "Admin":
        return {
            "id": user.id,
            "email": user.email,
            "role": user.role.value,
            "first_name": "SAID",
            "last_name": "CHOUCHF",
        }
        
    else:
        raise HTTPException(status_code=400, detail="Invalid User Role")
@auth_router.post("/forget-password")
async def forget_password(request : EmailRequest , db : Session = Depends(get_db)) :
    user = db.query(User).filter(User.email == request.email).first()
    if not user : 
        raise HTTPException(status_code=404, detail="email not found ")
    user.otp = str(random.randint(100000, 999999))
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=5)
    db.commit()

    message = MessageSchema(
        subject="Your Code",
        recipients=[request.email],
        template_body={"otp": user.otp},
        subtype=MessageType.html,
    )
    await fm.send_message(message, template_name="otp.html")

    return {"message": "we sent code into your account  "}



@auth_router.post("/change-password")
def change_password(request : ChangePasswordRequest ,user_id : int = Depends(get_current_user)   , db : Session = Depends(get_db)) :
    user = db.query(User).filter(User.id == user_id).first()
    if not user : 
        raise HTTPException(status_code=404, detail="user not found ")

    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="password not match ")
    user_password = get_password_hash(request.new_password)
    user.password = user_password
    db.commit()
    return {"message" : "password changed successfully "}
    

