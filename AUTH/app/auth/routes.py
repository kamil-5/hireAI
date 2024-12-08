from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db.database import get_db_connection
import bcrypt  # type: ignore

router = APIRouter()

# Charger les templates
templates = Jinja2Templates(directory="app/templates")

# Simuler une session utilisateur
user_session = {
    "is_logged_in": False,
    "username": None,
    "email": None,
    "role": None,
    "subscription": None,
    "subscription_name": None,
}

# Dépendances pour vérifier l'utilisateur connecté
def get_current_user():
    if not user_session["is_logged_in"]:
        raise HTTPException(status_code=401, detail="User not logged in.")
    return user_session

def admin_required(user_session: dict = Depends(get_current_user)):
    if user_session["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only.")
    return user_session

def candidate_required(user_session: dict = Depends(get_current_user)):
    if user_session["role"] != "candidate":
        raise HTTPException(status_code=403, detail="Access forbidden: Candidates only.")
    return user_session

# -------------------
# ROUTES COMMUNES
# -------------------

@router.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    """Afficher la page d'accueil."""
    return templates.TemplateResponse("index.html", {"request": request, "user": user_session})

@router.get("/login", response_class=HTMLResponse)
async def show_login(request: Request):
    """Afficher le formulaire de connexion."""
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    """Traiter la connexion des utilisateurs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT USERNAME, EMAIL, PASSWORD_HASH, ROLE, SUBSCRIPTION_ID FROM RECRUITAI_DB.PUBLIC.USERS WHERE EMAIL = %s",
            (email,)
        )
        result = cursor.fetchone()

        if result and bcrypt.checkpw(password.encode('utf-8'), result[2].encode('utf-8')):
            user_session.update({
                "is_logged_in": True,
                "username": result[0],
                "email": result[1],
                "role": result[3],
                "subscription": result[4],
                "subscription_name": "Basic" if result[4] == 1 else ("Pro" if result[4] == 2 else "Enterprise"),
            })

            return RedirectResponse(url="/", status_code=303)

        else:
            return templates.TemplateResponse("login.html", {"request": {}, "error_message": "Identifiants incorrects."})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de la connexion : {e}")
    finally:
        cursor.close()
        conn.close()

@router.get("/logout")
async def logout():
    """Déconnecter l'utilisateur."""
    user_session.update({
        "is_logged_in": False,
        "username": None,
        "email": None,
        "role": None,
        "subscription": None,
        "subscription_name": None,
    })
    return RedirectResponse(url="/")

# -------------------
# ROUTE SIGNUP
# -------------------

@router.get("/signup", response_class=HTMLResponse)
async def show_signup(request: Request):
    """Afficher le formulaire d'inscription."""
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup")
async def signup(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    profession: str = Form(...),  # Nouvelle entrée pour la profession
):
    """Créer un nouvel utilisateur avec une profession."""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO RECRUITAI_DB.PUBLIC.USERS (USERNAME, EMAIL, PASSWORD_HASH, ROLE, PROFESSION) VALUES (%s, %s, %s, 'candidate', %s)",
            (username, email, hashed_password, profession)
        )
        conn.commit()

        # Mise à jour de la session utilisateur
        user_session.update({
            "is_logged_in": True,
            "username": username,
            "email": email,
            "role": "candidate",
            "profession": profession,
            "subscription": None,
            "subscription_name": None,
        })

        return RedirectResponse(url="/subscriptions", status_code=303)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de l'inscription : {e}")
    finally:
        cursor.close()
        conn.close()


# -------------------
# ROUTES SUBSCRIPTION
# -------------------

@router.get("/subscriptions", response_class=HTMLResponse)
async def show_subscriptions(request: Request):
    """Afficher la liste des abonnements."""
    return templates.TemplateResponse(
        "subscriptions.html",
        {"request": request, "user": user_session, "subscription_types": ["Basic", "Pro", "Enterprise"]}
    )

@router.get("/subscribe/{subscription_type}", response_class=HTMLResponse)
async def select_subscription(subscription_type: str):
    """Sélectionner un abonnement."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Normaliser le type d'abonnement pour correspondre à la base de données
        subscription_type = subscription_type.capitalize()

        # Rechercher l'abonnement dans la table SUBSCRIPTIONS
        cursor.execute("SELECT ID FROM RECRUITAI_DB.PUBLIC.SUBSCRIPTIONS WHERE NAME = %s", (subscription_type,))
        subscription_id = cursor.fetchone()

        if not subscription_id:
            raise HTTPException(status_code=404, detail=f"Abonnement '{subscription_type}' introuvable.")

        # Mettre à jour l'utilisateur avec l'abonnement sélectionné
        cursor.execute(
            "UPDATE RECRUITAI_DB.PUBLIC.USERS SET SUBSCRIPTION_ID = %s WHERE EMAIL = %s",
            (subscription_id[0], user_session["email"])
        )
        conn.commit()

        # Mettre à jour la session utilisateur
        user_session.update({
            "subscription": subscription_id[0],
            "subscription_name": subscription_type,
        })

        # Rediriger vers le profil après la sélection
        return RedirectResponse(url="/profile", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de la sélection de l'abonnement : {e}")
    finally:
        cursor.close()
        conn.close()


# -------------------
# ROUTES CANDIDATS
# -------------------

@router.get("/candidate-dashboard", response_class=HTMLResponse)
async def candidate_dashboard(request: Request, user: dict = Depends(candidate_required)):
    """Tableau de bord candidat."""
    return templates.TemplateResponse("candidate_dashboard.html", {"request": request, "user": user})

@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, user: dict = Depends(get_current_user)):
    """Afficher le profil utilisateur."""
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})
