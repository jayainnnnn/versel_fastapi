from sqlalchemy import Column,String,Integer,Date
from database import Base


class Products(Base):
    __tablename__ = "products_data"
    product_id = Column(String, primary_key=True)
    product_url = Column(String, nullable=False)
    product_name = Column(String,nullable=False)
    product_price = Column(Integer,nullable=False)
    product_discount = Column(Integer,nullable=False)
    product_image = Column(Integer,nullable=False)
    date = Column(Date, nullable=False)
    product_max_price = Column(Integer,nullable=False)



