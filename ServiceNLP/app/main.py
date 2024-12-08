from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes import router

# Créer l'application FastAPI
app = FastAPI(title="Service NLP")

# Configurer les templates Jinja2
templates = Jinja2Templates(directory="app/templates")



# Inclure les routes
app.include_router(router)

# Point d'entrée simple pour tester le service
@app.get("/")
async def root():
    return {"message": "Bienvenue sur le service NLP"}
