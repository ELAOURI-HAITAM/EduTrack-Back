

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connexion import get_db
from middleware.auth import get_current_user
from models.notification import Notification


notification_router = APIRouter(
prefix="/notifications"
)


@notification_router.get("/")
def get_notifications(current_user = Depends(get_current_user) , db : Session = Depends(get_db)) :
    notifications = db.query(Notification).filter(Notification.user_id == current_user).order_by(Notification.created_at.desc()).all()
    return notifications


@notification_router.patch("/{notification_id}/read")
def read_notif(notification_id : int , current_user = Depends(get_current_user) , db : Session = Depends(get_db)) : 
    notif = db.query(Notification).filter(Notification.id == notification_id , Notification.user_id == current_user).first()
    if notif : 
        notif.is_read =True
        db.commit()
    return {"message" : "Notification marked as read"}