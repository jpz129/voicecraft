# FastAPI app entrypoint for Voicecraft
from fastapi import FastAPI
from app.api.routes import router
from app.config import configure_app

# Create FastAPI app instance
app = FastAPI(title="Voicecraft Revision API")

# Apply CORS and other configuration
configure_app(app)

# Register API routes (all endpoints are defined in app/api/routes.py)
app.include_router(router)
