from fastapi import FastAPI,HTTPException,Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,EmailStr
from datetime import date
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import and_

from model import Base,Products,new_products
from database import SessionLocal, engine


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from sqlalchemy.orm import Session
from datetime import date
from database import SessionLocal
from model import new_products,Products,product_ids

import re



app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class add_product(BaseModel):
    url : Annotated[str,Field(...,description="url of new product")]
    email : Annotated[EmailStr,Field(...,description="email of new person")]
@app.post("/addproduct")
def addproduct(add_url: add_product, db: Session = Depends(get_db)):
    product_id = re.search(r'/dp/([A-Z0-9]{10})', add_url.url).group(1)
    db.add(new_products(
        product_url = add_url.url,
        email = add_url.email,
        product_id = product_id
    ))
    db.commit()
    
    db.add(product_ids(
        product_id = product_id,
        url = add_url.url
    ))
    db.commit()

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    driver = webdriver.Chrome(options)
    driver.get(add_url.url)
    wait = WebDriverWait(driver,30)
    print(1)

    try:
        wait.until(EC.element_to_be_clickable((By.ID,"productTitle")))
        print(2)
        wait.until(EC.element_to_be_clickable((By.ID,"landingImage")))
        print(3)

        # wait.until(EC.element_to_be_clickable((By.CLASS_NAME,"a-price-whole")))
        # print(4)

        # price = driver.find_element(By.CLASS_NAME, "a-price-whole").text
        # price = int(price.replace(",", "").strip())
        # print(5)
        price_element = wait.until(EC.presence_of_element_located((
                By.XPATH,
                '//span[contains(@class,"priceToPay")]//span[@class="a-price-whole"]'
            )))
        price_text = price_element.text.strip().replace(",", "")
        price = int(price_text) if price_text else 0

        name = driver.find_element(By.ID, "productTitle").text.strip()
        image = driver.find_element(By.ID, "landingImage").get_attribute("src")
        today = date.today()
        print(6)
        new_data = Products(
        product_name = name,
        product_url = add_url.url,
        product_image = image,
        product_price = price,
        date = today,
        product_id = product_id
        )
        print(name,price,today)
        db.add(new_data)
        print(7)
    except TimeoutException:
        print(f"Element not found for index , skipping...")
    db.commit()
    db.close()



    return JSONResponse(status_code=201, content={"message": "URL ADDED SUCCESSFUL"})
