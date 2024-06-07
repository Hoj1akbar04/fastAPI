from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from models import Category, User
from database import session, ENGINE
from schemas import CategoryM
from fastapi_jwt_auth import AuthJWT

session = session(bind=ENGINE)
category_router = APIRouter(prefix="/categories")


@category_router.get("/")
async def get_categories(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    categories = session.query(Category).all()
    context = [
        {
            "id": category.id,
            "name": category.name,
        }
        for category in categories
    ]
    return jsonable_encoder(context)


@category_router.post("/create")
async def create_category(category: CategoryM, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    exist_users = session.query(User).filter(User.username == Authorize.get_jwt_subject()).first()
    if not exist_users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist")
    if exist_users.is_staff:
        check_category = session.query(Category).filter(Category.id == category.id).first()
        if check_category:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")

        new_category = Category(
            id=category.id,
            name=category.name
        )

        session.add(new_category)
        session.commit()

        context = {
            "status_code": 201,
            "msg": "category created"
        }
        return jsonable_encoder(context)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="not possible to create category data for you")


@category_router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_category(id: int, updated_category: CategoryM, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    exist_users = session.query(User).filter(User.username == Authorize.get_jwt_subject()).first()
    if not exist_users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist")
    if exist_users.is_staff:
        category = session.query(Category).filter_by(id=id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        category.name = updated_category.name

        session.commit()

        context = {
            "status_code": 200,
            "msg": "Category updated"
        }
        return jsonable_encoder(context)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="not possible to update category data for you")


@category_router.get("/{id}", status_code=status.HTTP_200_OK)
def get_category(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    check_category = session.query(Category).filter(Category.id == id).first()
    if check_category:
        context = {
            "id": check_category.id,
            "name": check_category.name
        }
        return jsonable_encoder(context)

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")


@category_router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_category(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    exist_users = session.query(User).filter(User.username == Authorize.get_jwt_subject()).first()
    if not exist_users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist")
    if exist_users.is_staff:
        category = session.query(Category).filter_by(id=id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        session.delete(category)
        session.commit()

        context = {
            "status_code": 200,
            "msg": "Category deleted"
        }
        return jsonable_encoder(context)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="not possible to delete category data for you")