from database import Base, ENGINE
from models import User, Category, Product, Order

Base.metadata.create_all(ENGINE)
