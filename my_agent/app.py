from fastapi import FastAPI
from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse
from .routers.wp_router import wp_router
app = FastAPI()

app.include_router(wp_router)
