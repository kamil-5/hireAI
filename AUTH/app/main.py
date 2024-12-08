from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.auth.routes import router as auth_router # Importer les routes d'authentification

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Charger les templates
templates = Jinja2Templates(directory="app/templates")

# Enregistrer les routes d'authentification
app.include_router(auth_router)

app.include_router(auth_router, prefix="/auth")