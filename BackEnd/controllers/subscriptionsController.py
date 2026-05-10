from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from database.connexion import get_db
from middleware.role import RoleChecker
from models.subscription import Subscription
from models.professor import Professor
from sqlalchemy.orm import Session, joinedload


subscription_router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"]
)


@subscription_router.post("/subscribe/{professor_id}")
def subscribe_teacher(
    professor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(RoleChecker("Student"))
):

    professor = db.query(Professor).filter(
        Professor.id == professor_id
    ).first()

    if not professor:
        raise HTTPException(
            status_code=404,
            detail="Professor not found"
        )

    existing_subscription = db.query(Subscription).filter(
        Subscription.student_id == current_user.student_data.id,
        Subscription.professor_id == professor_id
    ).first()

    if existing_subscription:
        raise HTTPException(
            status_code=400,
            detail="Already subscribed"
        )

    new_subscription = Subscription(
        student_id=current_user.student_data.id,
        professor_id=professor_id
    )

    db.add(new_subscription)
    db.commit()

    return {
        "message": "Subscribed successfully"
    }


@subscription_router.delete("/unfollow/{professor_id}")
def unfollow_teacher(
    professor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(RoleChecker("Student"))
):

    subscription = db.query(Subscription).filter(
        Subscription.student_id == current_user.student_data.id,
        Subscription.professor_id == professor_id
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )

    db.delete(subscription)
    db.commit()

    return {
        "message": "Unfollowed successfully"
    }

@subscription_router.get("/following")
def my_subscriptions(
    db: Session = Depends(get_db),
    current_user=Depends(RoleChecker("Student"))
):

    subscriptions = db.query(Subscription).options(
        joinedload(Subscription.professor)
    ).filter(
        Subscription.student_id == current_user.student_data.id
    ).all()

    return [
        {
            "subscription_id": sub.id,
            "professor_id": sub.professor.id,
            "first_name": sub.professor.first_name,
            "last_name": sub.professor.last_name,
            "email" : sub.professor.user.email,
            "phone" : sub.professor.phone_number
        }
        for sub in subscriptions
    ]

@subscription_router.get("/followers")
def professor_subscribers(
    db: Session = Depends(get_db),
    current_user=Depends(RoleChecker("Professor"))
):

    subscriptions = db.query(Subscription).options(
        joinedload(Subscription.student)
    ).filter(
        Subscription.professor_id == current_user.prof_data.id
    ).all()

    return [
        {
            "student_id": sub.student.id,
            "first_name": sub.student.first_name,
            "last_name": sub.student.last_name,
            "email" : sub.student.user.email,
            "gender" : sub.student.gender,
            "date" : sub.student.birth_date,
        }
        for sub in subscriptions
    ]