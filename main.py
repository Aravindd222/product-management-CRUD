from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from models import Product
from database import session, engine
from sqlalchemy.orm import Session
import database_models 


app = FastAPI()

#connect both frontend and backend in localhost 3000
#allowing cross origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"], #allow all methods get, post , put , delete
   # allow_headers=["*"], #Allow any custom headers sent from the frontend.
   # allow_credentials=True, #Turning this OFF breaks all login/authenticated APIs in browsers.
 
)

database_models.Base.metadata.create_all(bind=engine)

products = [
    Product(id=1, name="phone", description="budget phone", price=150.0, quantity=10),
    Product(id=2, name="tablet", description="budget tablet", price=250.0, quantity=8),
    Product(id=3, name="laptop", description="entry level laptop", price=550.0, quantity=5),
    Product(id=4, name="smartwatch", description="fitness smartwatch", price=120.0, quantity=15),
    Product(id=5, name="headphones", description="wireless headphones", price=80.0, quantity=20),
    Product(id=6, name="keyboard", description="mechanical keyboard", price=60.0, quantity=12),
    Product(id=7, name="mouse", description="gaming mouse", price=45.0, quantity=25)
]

def get_db():
    #db connection
    db=session()
    try:
        yield db
    finally:
        db.close()

def init_db():
    db = session()

    count = db.query(database_models.Product).count
    if count == 0:
        for product in products:
            #taking each product(pydantic) and 
            #converting to sqlalchemy model
            #then adding them to db but they accept only key value pairs
            #so we use model_dump to convert pydantic model to dict.
            #lastly to convert dict to key value pairs we use ** operator(unpacking)
            db.add(database_models.Product(**product.model_dump()))
            
    db.commit()
    db.close()
init_db()


''' @app.get("/")
def product():
    return "hello world" '''


@app.get("/products")
def get_all_products(db : Session = Depends(get_db)):
    
    # query 
    db_products = db.query(database_models.Product).all()
    return db_products

@app.get("/products/{id}")
def get_product_by_id(id: int, db : Session = Depends(get_db) ):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        return db_product 
    
    return "product not found"


    

@app.post("/products")
def add_product(product: Product, db : Session = Depends(get_db)):
    db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return "product added successfully"

@app.put("/products/{id}")
def update_product(id:int, product : Product,db : Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db_product.name = product.name
        db_product.description = product.description
        db_product.price = product.price
        db_product.quantity = product.quantity
        db.commit()
        return "product updated successfully"
    return "product not found"



@app.delete("/products/{id}")
def delete_product(id:int,db : Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return "product deleted successfully"
    return "product not found"



