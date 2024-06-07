from models import Order, Product, User
from schemas import OrderM, OrderUserM
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from database import session, ENGINE
from fastapi_jwt_auth import AuthJWT
session = session(bind=ENGINE)
orders_router = APIRouter(prefix="/orders")


@orders_router.get("/")
async def get_orders(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    orders = session.query(Order).all()
    context = [
        {
            "id": order.id,
            "user": {
                "id": order.users.id,
                "first_name": order.users.first_name,
                "last_name": order.users.last_name,
                "email": order.users.email,
                "username": order.users.username,
                "is_active": order.users.is_active,
                "is_staff": order.users.is_staff
            },
            "product": {
                "id": order.products.id,
                "name": order.products.name,
                "description": order.products.description,
                "price": order.products.price,
                "category": {
                    "id": order.products.categories.id,
                    "name": order.products.categories.name
                },
                "count": order.products.count
            },
            "order_status": order.order_status,
            "count": order.count
        }
        for order in orders
    ]

    return jsonable_encoder(context)


@orders_router.post("/create")
async def create_order(order: OrderM, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    exist_users = session.query(User).filter(User.username == Authorize.get_jwt_subject()).first()
    if not exist_users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist")
    if exist_users.is_staff:
        check_user = session.query(User).filter(User.id == order.user_id).first()
        check_product = session.query(Product).filter(Product.id == order.product_id).first()
        check_order = session.query(Order).filter(Order.id == order.id).first()

        if check_order:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order already exists")

        if check_product and check_user:
            new_order = Order(
                id=order.id,
                user_id=order.user_id,
                product_id=order.product_id,
                count=order.count,
                order_status=order.order_status
            )

            session.add(new_order)
            session.commit()
            context = [
                {
                    "status_code": 201,
                    "msg": "order created",
                    "data": {
                        "id": new_order.id,
                        "user": {
                            "id": new_order.users.id,
                            "first_name": new_order.users.first_name,
                            "last_name": new_order.users.last_name,
                            "email": new_order.users.email,
                            "username": new_order.users.username,
                            "is_active": new_order.users.is_active,
                            "is_staff": new_order.users.is_staff
                        },
                        "product": {
                            "id": new_order.products.id,
                            "name": new_order.products.name,
                            "description": new_order.products.description,
                            "price": new_order.products.price,
                            "category": {
                                "id": new_order.product.category.id,
                                "name": new_order.product.category.name
                            },
                            "count": new_order.products.count
                        },
                        "order_status": new_order.order_status,
                        "count": new_order.count
                    }
                }
            ]
            return jsonable_encoder(context)
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User_id or product_id already exists")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="not possible to create order data for you")


@orders_router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_order(id: int, updated_order: OrderM, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    order = session.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    check_user = session.query(User).filter(User.id == updated_order.user_id).first()
    check_product = session.query(Product).filter(Product.id == updated_order.product_id).first()

    if not check_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")

    if not check_product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product does not exist")

    order.user_id = updated_order.user_id
    order.product_id = updated_order.product_id

    session.commit()

    context = {
        "status_code": 200,
        "msg": "Order updated"
    }
    return jsonable_encoder(context)


@orders_router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_order(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    order = session.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    session.delete(order)
    session.commit()

    context = {
        "status_code": 200,
        "msg": "Order deleted"
    }
    return jsonable_encoder(context)


@orders_router.get("/{id}", status_code=status.HTTP_200_OK)
def get_orders(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    check_order = session.query(Order).filter(Order.id == id).first()
    if check_order:
        context = {
            "status_code": 201,
            "msg": "order created",
            "data": {
                "id": check_order.id,
                "user": {
                    "id": check_order.users.id,
                    "first_name": check_order.users.first_name,
                    "last_name": check_order.users.last_name,
                    "email": check_order.users.email,
                    "username": check_order.users.username,
                    "is_active": check_order.users.is_active,
                    "is_staff": check_order.users.is_staff
                },
                "product": {
                    "id": check_order.product.id,
                    "name": check_order.product.name,
                    "description": check_order.product.description,
                    "price": check_order.product.price,
                    "category": {
                        "id": check_order.product.category.id,
                        "name": check_order.product.category.name
                    },
                    "count": check_order.product.count
                },
                "order_status": check_order.order_status,
                "count": check_order.count,
                "total_b": check_order.product.price * check_order.count,
                "total_b_promokod": check_order.product.price * check_order
            }
        }
        promokod = "phone"
        if promokod == "phone":
            context["data"]["total_b_promokod"] *= 0.8
            return jsonable_encoder(context)

        else:
            return jsonable_encoder(context)

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")


@orders_router.post("/user/order")
async def get_order_user(order_user: OrderUserM, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    exist_users = session.query(User).filter(User.username == Authorize.get_jwt_subject()).first()
    if not exist_users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The user does not exist")
    if exist_users.is_staff:
        check_user = session.query(User).filter(User.username == order_user.username).first()
        if check_user and check_user.is_staff == True:
            check_order = session.query(Order).filter(Order.user_id == check_user.id)
            if check_order:
                context = [
                    {
                        "id": order.id,
                        "user": {
                            "id": order.users.id,
                            "first_name": order.users.first_name,
                            "last_name": order.users.last_name,
                            "email": order.users.email,
                            "username": order.users.username,
                            "is_active": order.users.is_active,
                            "is_staff": order.users.is_staff
                        },
                        "product": {
                            "id": order.products.id,
                            "name": order.products.name,
                            "description": order.products.description,
                            "price": order.products.price,
                            "category": {
                                "id": order.products.categories.id,
                                "name": order.products.categories.name
                            },
                            "count": order.products.count
                        },
                        "order_status": order.order_status,
                        "count": order.count
                    }
                    for order in check_order
                ]
                return jsonable_encoder(context)
            return HTTPException(status_code=status.HTTP_200_OK, detail="This user has no orders")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found this user")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not possible to view order/user data for you")



@orders_router.post("/user/order/price")
async def user_order_price(order_user: OrderUserM, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")
    check_user = session.query(User).filter(User.username == order_user.username).first()
    if check_user:
        check_order = session.query(Order).filter(Order.user_id == check_user.id)
        if check_order:
            total_price = 0
            product_count = 0
            for order in check_order:
                total_price += order.count * order.products.price

            data = {
                "status code": 200,
                "msg": "The total price",
                "data": {
                    "total_price": total_price,
                    "product_count": product_count
                }
            }
            return jsonable_encoder(data)

