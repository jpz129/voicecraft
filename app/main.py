from fastapi import FastAPI
from app.api.routes import router
from app.config import configure_app

app = FastAPI(title="Voicecraft Revision API")
configure_app(app)
app.include_router(router)
