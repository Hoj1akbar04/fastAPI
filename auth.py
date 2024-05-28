from fastapi import APIRouter, HTTPException, status
from database import session, ENGINE
from models import User
from werkzeug import security
from schemas import Registration, Login

session = session(bind=ENGINE)
auth_router = APIRouter(prefix="/auth")


@auth_router.get("/login")
async def login():
    return {
        "message": "Login Page"
    }


@auth_router.post("/login")
async def login(user: Login):
    username = session.query(User).filter(User.username == user.username).first()
    if username is None:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Username error")

    user_check = session.query(User).filter(User.username == user.username).first()
    if security.check_password_hash(user_check.password, user.password):
        return HTTPException(status_code=status.HTTP_200_OK, detail=f"Login Successful {user.username}")

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid username or password")



@auth_router.get("/register")
async def register():
    return {
        "message": "Register Page"
    }


@auth_router.post("/register")
async def register(user: Registration):
    username = session.query(User).filter(User.username == user.username).first()
    email = session.query(User).filter(User.email == user.email).first()
    if username is not None or email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A user with such email and username already exists")

    new_user = User(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        password=security.generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff
    )

    session.add(new_user)
    session.commit()
    return HTTPException(status_code=status.HTTP_201_CREATED, detail="Successfully registered")






@auth_router.get("/logout")
async def get_logout():
    return {
        "message": "Logout Page"
    }



@auth_router.post("/logout")
async def logout():
    return {
        "message": "Logout successful"
    }
