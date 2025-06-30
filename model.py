from sqlalchemy import Column,String,Integer,Date,LargeBinary
from database import Base


class Products(Base):
    __tablename__ = "products_data"
    product_name = Column(String, nullable=False)
    product_url = Column(String, nullable=False)
    product_image = Column(String,nullable=False)
    product_price = Column(Integer,nullable=False)
    date = Column(Date, nullable=False)
    product_id = Column(Integer,nullable=False)
    id = Column(Integer, primary_key=True, autoincrement=True)
class new_products(Base):
    __tablename__ = "user_urls"
    product_url = Column(String,nullable=False)
    email = Column(String,nullable=False)
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer,nullable=False)



