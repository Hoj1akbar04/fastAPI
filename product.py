from fastapi import APIRouter, HTTPException, status
from database import ENGINE, session
from models import Category, Product
from fastapi.encoders import jsonable_encoder
from schemas import ProductM

session = session(bind=ENGINE)
product_router = APIRouter(prefix="/products")


@product_router.get("/")
def get_products():
    products = session.query(Product).all()
    context = [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "category_id": product.category_id,
        }
        for product in products
    ]

    return jsonable_encoder(context)


@product_router.post("/create")
def create_product(product: ProductM):
    check_product = session.query(Product).filter(Product.id == product.id).first()
    check_category = session.query(Category).filter(Category.id == product.category_id).first()
    if check_product:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product already exist")

    if check_category:
        new_product = Product(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            category_id=product.category_id
        )

        session.add(new_product)
        session.commit()
        context = {
            "status_code": 201,
            "msg": "product created"
        }
        return jsonable_encoder(context)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="category_id already exists")


@product_router.put("/update/{product_id}", status_code=status.HTTP_200_OK)
def update_product(product_id: int, updated_product: ProductM):
    product = session.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    product.name = updated_product.name
    product.description = updated_product.description
    product.price = updated_product.price
    product.category_id = updated_product.category_id

    session.commit()

    context = {
        "status_code": 200,
        "msg": "Product updated"
    }
    return jsonable_encoder(context)


@product_router.delete("/delete/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(product_id: int):
    product = session.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    session.delete(product)
    session.commit()

    context = {
        "status_code": 200,
        "msg": "Product deleted"
    }
    return jsonable_encoder(context)