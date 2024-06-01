from models import Order, Product, User
from schemas import OrderM
from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from database import session, ENGINE

session = session(bind=ENGINE)
orders_router = APIRouter(prefix="/orders")


@orders_router.get("/")
async def get_orders():
    orders = session.query(Order).all()
    context = [
        {
            "id": order.id,
            "user_id": order.user_id,
            "product_id": order.product.id,

        }
        for order in orders
    ]

    return jsonable_encoder(context)


@orders_router.post("/create")
async def create_order(order: OrderM):
    check_user = session.query(User).filter_by(User.id == order.user_id).first()
    check_product = session.query(Product).filter_by(Product.id == order.product.id).first()
    check_order = session.query(Order).filter_by(Order.id == order.id).first()

    if check_order:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order already exists")

    if check_product and check_user:
        new_order = Order(
            id=order.id,
            user_id=order.user_id,
            product_id=order.product.id
        )

        session.add(new_order)
        session.commit()
        context = {
            "status_code": 201,
            "msg": "order created"
        }
        return jsonable_encoder(context)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User_id or product_id already exists")


@orders_router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_order(id: int, updated_order: OrderM):
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
async def delete_order(id: int):
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
def get_orders(id: int):
    check_order = session.query(Order).filter(Order.id == id).first()
    if check_order:
        context = {
            "id": check_order.id,
            "user_id": check_order.user_id,
            "product_id": check_order.product_id
        }
        return jsonable_encoder(context)

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
