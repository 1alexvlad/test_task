from fastapi import FastAPI
from routers.user import router as user_router
from routers.admin import router as admin_router
from routers.webhooks import router as webhook_router

app = FastAPI()

app.include_router(user_router)
app.include_router(admin_router)
app.include_router(webhook_router)
