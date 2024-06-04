from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder

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


@auth_router.get("/users")
async def get_users():
    users = session.query(User).all()
    data = [
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
            "is_staff": user.is_staff
        }
        for user in users
    ]
    return jsonable_encoder(data)


@auth_router.post("/users/create")
async def create_user(user: Registration):
    check_user = session.query(User).filter(User.id == user.id).first()
    if check_user:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exist")

    new_user = User(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        is_staff=user.is_staff
    )

    session.add(new_user)
    session.commit()

    data = {
        "status_code": 201,
        "msg": "user created",
        "data": {
            "id": new_user.id,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email": new_user.email,
            "username": new_user.username,
            "is_active": new_user.is_active,
            "is_staff": new_user.is_staff
        }
    }
    return jsonable_encoder(data)


@auth_router.get("/users/{id}")
async def read_user(id: int):
    check_user = session.query(User).filter(User.id == id).first()
    if check_user:
        data = {
            "id": check_user.id,
            "first_name": check_user.first_name,
            "last_name": check_user.last_name,
            "email": check_user.email,
            "username": check_user.username,
            "is_active": check_user.is_active,
            "is_staff": check_user.is_staff
        }

        return jsonable_encoder(data)
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")


@auth_router.put("/users/{id}", status_code=status.HTTP_200_OK)
async def update_user(id: int, data: Registration):
    user = session.query(User).filter(User.id == id).first()
    if user:
        for key, value in data.dict(exclude_unset=True).items():
            setattr(user, key, value)

        session.commit()
        data = {
            "status_code": 200,
            "msg": "Product updated"
        }
        return jsonable_encoder(data)
    else:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed!")


@auth_router.delete("/users/{id}", status_code=status.HTTP_200_OK)
def delete_product(id: int):
    user = session.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    session.delete(user)
    session.commit()

    context = {
        "status_code": 200,
        "msg": "User deleted"
    }
    return jsonable_encoder(context)


