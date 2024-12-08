import jwt
from fastapi import HTTPException

SECRET_KEY = "votre_clé_secrète"  # Remplacez ceci par une clé secrète plus robuste
ALGORITHM = "HS256"  # L'algorithme de chiffrement utilisé

def verify_token(token: str):
    try:
        # Décoder le token et vérifier sa validité
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
