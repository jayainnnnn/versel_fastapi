from fastapi import FastAPI,HTTPException,Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,EmailStr
from datetime import date
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import and_

from model import Base,Products
from database import SessionLocal, engine


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


import re
import time



app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class add_product(BaseModel):
    product_id : Annotated[str,Field(...,description="id of new product")]
    product_url : Annotated[str,Field(...,description="url of new product")]
@app.post("/addproduct")
def addproduct(add_id: add_product, db: Session = Depends(get_db)):

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    driver = webdriver.Chrome(options=options)
    driver.get(add_id.product_url)
    wait = WebDriverWait(driver,30)
    print(1)
    try:
        wait.until(EC.element_to_be_clickable((By.ID,"productTitle")))
        print(2)
        wait.until(EC.element_to_be_clickable((By.ID,"landingImage")))
        print(3)
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
            product_id = add_id.product_id,
            product_url = add_id.product_url,
            product_name = name,
            product_price = price,
            product_discount = 0,
            product_image = image,
            date = today,
            product_max_price = price
        )
        db.add(new_data)
        db.commit()
        return JSONResponse(status_code=200, content={
            "status": "success",
            "product_id": new_data.product_id,
            "product_name": new_data.product_name,
            "product_price": new_data.product_price,
            "product_image": new_data.product_image
        })
    except TimeoutException:
        return JSONResponse(status_code=400, content={
            "status": "failed"
        })
    finally:
        driver.quit()


class search_product(BaseModel):
    name : Annotated[str,Field(...,description="name of new product")]
    email : Annotated[EmailStr,Field(...,description="email of person")]

@app.post('/searchproduct')
def search_products(searchquery: search_product, db: Session = Depends(get_db)):
    product_name = searchquery.name

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    wait = WebDriverWait(driver, 10)

    search_url = f"https://www.amazon.in/s?k={product_name}"
    results = []
    driver.get(search_url)
    max_attempts = 3

    for attempt in range(max_attempts):
        
        driver.get(search_url)

        products = driver.find_elements(By.CSS_SELECTOR, 'div.s-widget-container[data-csa-c-type="item"]')
        for product in products:
            try:
                title = product.find_element(By.CSS_SELECTOR, 'a.a-link-normal.a-text-normal').text
                link = product.find_element(By.CSS_SELECTOR, 'a.a-link-normal').get_attribute('href')
                product_id = re.search(r'/dp/([A-Z0-9]{10})', link).group(1)
                img = product.find_element(By.CSS_SELECTOR, 'img.s-image').get_attribute('src')
                price = product.find_element(By.CSS_SELECTOR, 'span.a-price-whole').text
                print(f"Title: {title}\nLink: {link}\nImage: {img}\nPrice: ₹{price}\n---")
            except:
                continue

            results.append({
                    "title": title,
                    "product_id": product_id,
                    "image": img,
                    "price": price
            })

            if len(results) >= 50:
                break  

        if results:
            driver.quit()
            return JSONResponse(status_code=200, content=results)
        print(attempt)
    driver.quit()
    return JSONResponse(status_code=404,content={"message":"NO PRODUCTS FOUND"})



