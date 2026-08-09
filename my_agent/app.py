from fastapi import FastAPI
from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from .routers.wp_router import wp_router
from .routers.customer_router import order_rotuer
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "https://ecorinse.sumankumarsahu7890.workers.dev"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wp_router)
app.include_router(order_rotuer)
