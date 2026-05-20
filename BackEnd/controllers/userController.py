


import pandas as pd
import io
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from database.connexion import get_db
from middleware.role import RoleChecker
from models.notification import Notification
from models.user import User
from validations.userSchema import UpdateUserInfosRequest, createUserRequest


user_router = APIRouter(
    prefix="/users"
)





@user_router.post("/create")
def create_user(request : createUserRequest , current_user = Depends(RoleChecker("Admin")) , db : Session = Depends(get_db)) : 
    user = db.query(User).filter(User.email == request.email).first();
    if user : 
        raise HTTPException(status_code=400 , detail = "this Email Already Exists")
    new_user = User(
        email = request.email,
        role = request.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message" : "User Created Successfully" , "user" : new_user}



@user_router.get("/all")
def get_all_users(current_user = Depends(RoleChecker("Admin")) , db : Session = Depends(get_db)) : 
    users = db.query(User).filter(User.role != "Admin" ).all()
    result = []

    for user in users : 
        first_name = "",
        last_name = ""
        gender = ""
        birth_date = None
        if user.role.value == "Student" and user.student_data : 
            first_name = user.student_data.first_name 
            last_name = user.student_data.last_name 
            gender = user.student_data.gender 
            birth_date = user.student_data.birth_date
        elif user.role.value == "Professor" and user.prof_data : 
            first_name = user.prof_data.first_name 
            last_name = user.prof_data.last_name 
            gender = user.prof_data.gender 
            birth_date = user.prof_data.birth_date
        result.append({
            "id": user.id,
            "email": user.email,
            "role": user.role.value,
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "birth_date": birth_date.isoformat() if birth_date else None,
            "status": "Active" if user.password else "Pending" 
        })
    return result



@user_router.put("/update/{user_id}")
def update_user(
    user_id: int, 
    request: UpdateUserInfosRequest, 
    current_user = Depends(RoleChecker("Admin")), 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if request.email and request.email != user.email:
        if user.password: 
            raise HTTPException(
                status_code=400, 
                detail="Cannot change email. This account is already Active."
            )
        
        email_exists = db.query(User).filter(User.email == request.email).first()
        if email_exists:
            raise HTTPException(status_code=400, detail="This email is already in use")
            
        user.email = request.email 

    req_role_str = request.role.value if hasattr(request.role, 'value') else request.role
    db_role_str = user.role.value if hasattr(user.role, 'value') else user.role

    if req_role_str and req_role_str != db_role_str: 
        if user.password: 
            raise HTTPException(
                status_code = 400, 
                detail = "Cannot change role. This account is already Active."
            )
        
        user.role = request.role

    current_role_str = user.role.value if hasattr(user.role, 'value') else user.role

    if current_role_str == "Student" and user.student_data:
        if request.first_name: user.student_data.first_name = request.first_name
        if request.last_name: user.student_data.last_name = request.last_name
        if request.gender: user.student_data.gender = request.gender
        if request.birth_date: user.student_data.birth_date = request.birth_date

    elif current_role_str == "Professor" and user.prof_data:
        if request.first_name: user.prof_data.first_name = request.first_name
        if request.last_name: user.prof_data.last_name = request.last_name
        if request.gender: user.prof_data.gender = request.gender
        if request.birth_date: user.prof_data.birth_date = request.birth_date
        if request.phone_number: user.prof_data.phone_number = request.phone_number
        
    else:
        if request.first_name or request.last_name or request.gender:
            raise HTTPException(
                status_code=400, 
                detail="Cannot update profile info (First name, Last name, Gender) because this user hasn't completed registration yet."
            )

    db.commit()
    
    return {"message": "User updated successfully"}




@user_router.delete("/delete/{user_id}")
def delete_user(user_id : int , current_user = Depends(RoleChecker("Admin")) , db : Session = Depends(get_db)) : 
    user = db.query(User).filter(User.id == user_id).first()
    if  not user : 
        raise HTTPException(status_code=404 , detail="User Not Found")
    db.query(Notification).filter(
        (Notification.sender_id == user.id) | (Notification.receiver_id == user.id)
    ).delete(synchronize_session=False)
    db.delete(user)
    db.commit()

    return {"message" : "User Deleted Successfully"}


@user_router.get("/details/{user_id}")
def get_user_details(user_id : int , current_user = Depends(RoleChecker("Admin")) , db : Session = Depends(get_db)) : 
    user = db.query(User).filter(User.id == user_id).first()
    if not user : 
        raise HTTPException(status_code = 404 , detail = "User Not Found")
    first_name = ""
    last_name = ""
    gender = ""
    birth_date = ""
    if user.role.value == "Student" and user.student_data : 
        first_name = user.student_data.first_name
        last_name = user.student_data.last_name
        gender = user.student_data.gender
        birth_date = user.student_data.birth_date
    elif user.role.value == "Professor" and user.prof_data : 
            first_name = user.prof_data.first_name 
            last_name = user.prof_data.last_name 
            gender = user.prof_data.gender 
            birth_date = user.prof_data.birth_date
    return {
        "id" : user.id,
        "first_name" : first_name,
        "last_name" : last_name,
        "gender" : gender,
        "birth_date" : birth_date,
        "role" : user.role.value,
        "email" : user.email
    }


@user_router.post("/import-excel")
async def import_users_from_excel(
    file: UploadFile = File(...),
    current_user = Depends(RoleChecker("Admin")), 
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="just excel files (xls , xlsx)"
        )

    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        df.columns = [str(col).strip().lower() for col in df.columns]

        if 'email' not in df.columns or 'role' not in df.columns:
            raise HTTPException(
                status_code=404, 
                detail="email and role column not found !!"
            )

        success_count = 0
        skipped_emails = []

        for index, row in df.iterrows():
            email = str(row['email']).strip()
            role = str(row['role']).strip()

            if pd.isna(row['email']) or pd.isna(row['role']):
                continue

            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                skipped_emails.append({"email": email, "reason": "already exists"})
                continue 

            if role not in ["Student", "Professor"]:
                skipped_emails.append({"email": email, "reason": f"this role :  '{role}' not usable "})
                continue

            new_user = User(
                email=email,
                role=role,
                password=None, 
                otp=None,
                otp_expires_at=None
            )
            db.add(new_user)
            success_count += 1

        if success_count > 0:
            db.commit()

        return {
            "message": "Users Are Created Successfully",
            "created_users_count": success_count,
            "skipped_users": skipped_emails
        }

    except Exception as e:
        db.rollback() 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Something Went Wrong {str(e)}"
        ) 