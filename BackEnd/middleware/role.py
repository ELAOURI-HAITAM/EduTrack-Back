from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database.connexion import get_db
from middleware.auth import get_current_user
from models.user import User


def RoleChecker(required_role: str):

    def checker(
        current_user_id: int = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

        user = db.query(User).filter(
            User.id == current_user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        if user.role.value != required_role:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource"
            )

        return user

    return checker