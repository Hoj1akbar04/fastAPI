from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder

from database import session, ENGINE
from models import User
from werkzeug import security
from schemas import Registration, Login
from fastapi_jwt_auth import AuthJWT
session = session(bind=ENGINE)
auth_router = APIRouter(prefix="/auth")


@auth_router.get("/login",)
async def login():
    return {
        "message": "Login Page"
    }


@auth_router.post("/login")
async def login(user: Login, Authorize: AuthJWT=Depends()):
    check_user = session.query(User).filter(User.username == user.username).first()
    if check_user and security.check_password_hash(check_user.password, user.password):
        access_token = Authorize.create_access_token(subject=check_user.username)
        refresh_token = Authorize.create_refresh_token(subject=check_user.username)
        data = {
            "success": True,
            "code": 200,
            "msg": "Successful Login",
            "user": {
                "username": user.username,
            "token": {
                "access_token": access_token,
                "refresh_token": refresh_token
                }
            }
        }
        return jsonable_encoder(data)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"username or password error")


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
async def get_users(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    exist_users = session.query(User).filter(User.username == Authorize.get_jwt_subject()).first()
    if not exist_users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist")
    if exist_users.is_staff:
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
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="don't create")


@auth_router.post("/users/create")
async def create_user(user: Registration, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    exist_users = session.query(User).filter(User.username == Authorize.get_jwt_subject()).first()
    if not exist_users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist")
    if exist_users.is_staff:
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
async def read_user(id: int, Authorize: AuthJWT = Depends()):
    exist_user = session.query(User).filter(User.username == Authorize.get_jwt_subject()).first()
    if not exist_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This user does not exist")
    if exist_user.is_staff:
        check_user = session.query(User).filter(User.id == id).first()
        if check_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        context = {
            "id": check_user.id,
            "first_name": check_user.first_name,
            "last_name": check_user.last_name,
            "email": check_user.email,
            "username": check_user.username,
            "is_active": check_user.is_active,
            "is_staff": check_user.is_staff
        }

        return jsonable_encoder(context)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")


@auth_router.put("/users/{id}", status_code=status.HTTP_200_OK)
async def update_user(id: int, data: Registration, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    exist_user = session.query(User).filter(User.username == Authorize.get_jwt_subject()).first()
    if not exist_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist")
    if exist_user.is_staff:
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed!")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed!")


@auth_router.delete("/users/{id}", status_code=status.HTTP_200_OK)
def delete_product(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    exist_user = session.query(User).filter(User.username == Authorize.get_jwt_subject()).first()
    if not exist_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist")
    if exist_user.is_staff:
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
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="don't view!")


