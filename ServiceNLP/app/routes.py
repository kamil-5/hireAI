from fastapi import APIRouter, HTTPException, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.db.database import get_db_connection
from app.nlp.utils import analyze_cv_with_chunks, extract_skills_from_offers
import os

# Initialisation du routeur et des templates
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    """Afficher la page principale."""
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/offers", response_class=HTMLResponse)
async def view_offers(request: Request):
    """Afficher les offres d'emploi disponibles."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT JOB_TITLE, COMPANY_NAME, REQUIRED_SKILLS, JOB_DESCRIPTION
                FROM RECRUITAI_DB.PUBLIC.JOB_OFFERS
            """)
            offers = [
                {
                    "job_title": row[0] or "Non spécifié",
                    "company_name": row[1] or "Non spécifié",
                    "required_skills": row[2] or "Non spécifié",
                    "description": row[3] or "Non spécifié"
                }
                for row in cursor.fetchall()
            ]
        return templates.TemplateResponse("view_offers.html", {"request": request, "offers": offers})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des offres : {e}")
    finally:
        conn.close()

@router.get("/upload_cv", response_class=HTMLResponse)
async def upload_cv_page(request: Request):
    """Afficher la page de dépôt de CV."""
    return templates.TemplateResponse("upload_cv.html", {"request": request})

@router.post("/upload_cv", response_class=HTMLResponse)
async def upload_cv(request: Request, file: UploadFile):
    """Déposer et analyser un CV."""
    file_path = f"uploaded_cvs/{file.filename}"
    try:
        # Créer le dossier si nécessaire
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Sauvegarder le fichier localement
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Analyse du CV pour extraire les compétences
        skills = analyze_cv_with_chunks(file_path)

        # Retourner le template avec les résultats
        return templates.TemplateResponse("upload_cv.html", {
            "request": request,
            "message": "CV téléchargé et analysé avec succès",
            "skills": skills
        })
    except Exception as e:
        return templates.TemplateResponse("upload_cv.html", {
            "request": request,
            "message": f"Erreur lors du téléchargement du CV : {e}",
            "skills": []
        })

@router.get("/analyze_offers", response_class=HTMLResponse)
async def analyze_offers_page(request: Request):
    """Analyser les compétences des offres d'emploi."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT JOB_TITLE, COMPANY_NAME, REQUIRED_SKILLS
                FROM RECRUITAI_DB.PUBLIC.JOB_OFFERS
            """)
            data = [
                {
                    "job_title": row[0] or "Non spécifié",
                    "company": row[1] or "Entreprise inconnue",
                    "required_skills": row[2] or ""
                }
                for row in cursor.fetchall()
            ]

        # Analyse des compétences pour chaque offre
        analysis = []
        for offer in data:
            skills = extract_skills_from_offers([{
                "description": offer["required_skills"],
                "company": offer["company"]
            }])
            analysis.append({
                "job_title": offer["job_title"],
                "company": offer["company"],
                "skills": skills[0]["skills"] if skills else ["Aucune compétence détectée"]
            })

        return templates.TemplateResponse("analyze_results.html", {"request": request, "analysis": analysis})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse des offres : {e}")
    finally:
        conn.close()
