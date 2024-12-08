from fastapi import HTTPException, Depends
from app.auth.security import verify_token
from app.auth.models import User
from fastapi import Request

from app.db.database import get_db_connection

# Dépendance pour obtenir l'utilisateur connecté
def get_current_user(request: Request):
    token = request.cookies.get("access_token")  # Exemple avec cookies
    if not token:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    user_id = verify_token(token)  # Cette fonction devra décoder le token et récupérer l'ID de l'utilisateur
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Rechercher l'utilisateur dans la base de données
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USERS WHERE USER_ID = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(**user)  # Assurez-vous d'avoir une classe Pydantic User qui mappe les données de l'utilisateur
