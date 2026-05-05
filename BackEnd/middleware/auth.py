import os
from fastapi import Depends, HTTPException, status , Request
from fastapi.security import OAuth2PasswordBearer as OA
from dotenv import load_dotenv
import jwt
from models.user import User
load_dotenv()
from database.connexion import get_db
from sqlalchemy.orm import Session
oauth2_scheme = OA(tokenUrl="users/verify-otp")
secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")



def get_current_user(request: Request, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token credentials",
    )
    
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated (No Cookie found)"
        )

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id: int = payload.get("id")
        
        if user_id is None:
            raise credentials_exception
            
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    return user.id
