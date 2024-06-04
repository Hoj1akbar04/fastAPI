from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types.choice import ChoiceType

from database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(30), nullable=True)
    last_name = Column(String(30), nullable=True)
    email = Column(Text, nullable=True)
    username = Column(String(30), unique=True, nullable=True)
    password = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)
    orders = relationship("Order", back_populates="users")

    def __repr__(self):
        return self.username


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=True)
    products = relationship("Product", back_populates="categories")

    def __repr__(self):
        return self.name


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=True)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    count = Column(Integer, nullable=False)
    categories = relationship('Category', back_populates='products')
    orders = relationship("Order", back_populates="products")

    def __repr__(self):
        return self.name


class Order(Base):
    __tablename__ = 'orders'
    OrderChoices = (
        ("PANDING", "panding"),
        ("TRANSIT", "transit"),
        ("DELIVERED", "delivered")
    )
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship('User', back_populates="orders")
    product_id = Column(Integer, ForeignKey('products.id'))
    products = relationship('Product', back_populates="orders")
    order_status = Column(ChoiceType(choices=OrderChoices), default="Pending")
    count = Column(Integer, nullable=False)




