from fastapi import  FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host = "redis-14724.c309.us-east-2-1.ec2.cloud.redislabs.com",
    port = 14724,
    password = "S2nHPHtr0kuDcpzGRoZgP0oCC2fthpgj",
    decode_responses = True
)

class Product(HashModel):
    name:str
    price:int
    # quantity available
    quantity:int

    class Meta:
        database = redis

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

@app.get('/products')
def all():
    return [format(pk) for pk in Product.all_pks()]

def format(pk:str):
    product = Product.get(pk)

    return {
        'id':product.pk,
        'name':product.name,
        'price':product.price,
        'quantity':product.quantity
    }

@app.post('/products')
def create(product:Product):
    return product.save()

@app.get('/products/{pk}')
def get(pk:str):
    return Product.get(pk)

@app.delete('/products/{pk}')
def delete(pk:str):
    return Product.delete(pk)