# app/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Informations sur le token
SECRET_KEY = "your_secret_key"  # Changez cette clé pour la rendre plus sécurisée
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Expiration du token en minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Fonction pour générer un token JWT
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dépendance pour vérifier le token et extraire l'utilisateur actuel
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email  # Retourner l'email comme preuve que le token est valide
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
