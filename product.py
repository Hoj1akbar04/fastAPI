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
    if (check_product and check_category) or (check_product and check_category is None):
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
            "msg": "product created",
            "data": {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "category_id": product.category_id,
            }
        }
        return context
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="category_id already exists")


@product_router.get("/{id}")
async def get_product(id: int):
    check_product = session.query(Product).filter(Product.id == id).first()
    if check_product:
        context = [
            {
                "id": check_product.id,
                "name": check_product.name,
                "description": check_product.description,
                "price": check_product.price,
                "category_id": check_product.category_id,
            }
        ]
        return jsonable_encoder(context)
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product not found")


@product_router.put("/{id}", status_code=status.HTTP_200_OK)
def update_product(id: int, data: ProductM):
    product = session.query(Product).filter(Product.id == id).first()
    check_category = session.query(Category).filter(Category.id == data.category_id).first()
    if product:
        if check_category:
            for key, value in data.dict(exclude_unset=True).items():
                setattr(product, key, value)

            session.commit()
            context = {
                "status_code": 200,
                "msg": "Product updated"
            }
            return jsonable_encoder(context)
        else:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed!")

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed!")


@product_router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_product(id: int):
    product = session.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    session.delete(product)
    session.commit()

    context = {
        "status_code": 200,
        "msg": "Product deleted"
    }
    return jsonable_encoder(context)