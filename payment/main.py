import time

from fastapi import  FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import requests
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

class Order(HashModel):
    product_id:str
    price:float
    fee:float
    total:float
    quantity:int
    status:str #pending, completed, refunded

    class Meta:
        database = redis

@app.get('/orders/{pk}')
def get(pk:str):
    return Order.get(pk)


@app.post('/orders')
async def create(request:Request, background_tasks:BackgroundTasks): #id, quantity
    body = await request.json()

    req = requests.get('http://localhost:8000/products/%s' % body['id'])
    product = req.json()
    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2*product['price'],
        total=1.2*product['price'],
        quantity=body['quantity'],
        status='pending'
    )
    order.save()
    background_tasks.add_task(order_completed,order)
    return order

def order_completed(order:Order):
    time.sleep(5)
    order.status='completed'
    order.save()
    redis.xadd('order_completed', order.dict(),'*')

