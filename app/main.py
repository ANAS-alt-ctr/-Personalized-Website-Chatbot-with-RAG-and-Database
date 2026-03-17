from fastapi import FastAPI
from app.routes.auth_routes import router as auth_router
from app.routes.chat_routes import router as chat_router
from app.routes.website_routes import router as web_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(web_router)
app.include_router(chat_router)