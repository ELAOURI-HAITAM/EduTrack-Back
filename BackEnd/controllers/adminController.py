from ast import Module
from asyncio import Task
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.connexion import get_db
from middleware.role import RoleChecker
from models.notification import Notification
from utils.hash import get_password_hash
from validations.notificationSchema import BroadCastNotification
from models.user import User
from models.module import Module
from models.task import Task
admin_router = APIRouter(
    prefix ="/admin"
)







@admin_router.get("/my-stats")
def get_dashboard_stats(
    current_user = Depends(RoleChecker("Admin")), 
    db: Session = Depends(get_db)
):
    total_students = db.query(User).filter(User.role == "Student", User.password.isnot(None)).count()
    
    total_professors = db.query(User).filter(User.role == "Professor",User.password.isnot(None)).count()
    
    active_accounts = db.query(User).filter(User.password != None, User.role != "Admin").count()
    pending_accounts = db.query(User).filter(User.password == None, User.role != "Admin").count()
    
    total_modules = db.query(Module).count()
    total_tasks = db.query(Task).count()

    return {
        "users": {
            "total_students": total_students,
            "total_professors": total_professors,
            "total_users": total_students + total_professors
        },
        "account_status": {
            "active": active_accounts,
            "pending": pending_accounts
        },
        "content": {
            "total_modules": total_modules,
            "total_tasks": total_tasks
        }
    }



