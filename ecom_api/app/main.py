from fastapi import FastAPI
from app.routers import items

app=FastAPI(title="Ecom Summary API")

#include routers
app.include_router(items.router)