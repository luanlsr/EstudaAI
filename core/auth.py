from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi_sso.sso.google import GoogleSSO
from jose import jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "minha_super_senha_secreta_jwt_123")
ALGORITHM = "HS256"

# Descobrir automaticamente a URL base baseada no ambiente
RAILWAY_PUBLIC_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
if RAILWAY_PUBLIC_DOMAIN:
    callback_url = f"https://{RAILWAY_PUBLIC_DOMAIN}/auth/google/callback"
else:
    # Fallback para desenvolvimento local. Vercel e Railway lidam com suas proprias env vars.
    callback_url = "http://localhost:8000/auth/google/callback"

google_sso = GoogleSSO(
    client_id=os.environ.get("GOOGLE_CLIENT_ID", ""),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET", ""),
    redirect_uri=callback_url,
    allow_insecure_http=True
)

auth_router = APIRouter(prefix="/auth/google", tags=["Auth"])

@auth_router.get("/login")
async def google_login():
    """Redirect to Google for authentication."""
    with google_sso:
        return await google_sso.get_login_redirect()

@auth_router.get("/callback")
async def google_callback(request: Request, response: Response):
    """Process login response from Google and return a JWT cookie."""
    try:
        with google_sso:
            user = await google_sso.verify_and_process(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro na autenticação: {str(e)}")

    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = {
        "sub": user.email,
        "name": user.display_name,
        "picture": user.picture,
        "exp": expire
    }
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # Redireciona o usuário para a página principal, setando o cookie
    response = Response(status_code=302)
    response.headers["Location"] = "/"
    response.set_cookie(key="access_token", value=token, httponly=True, secure=True, samesite="lax", max_age=7*24*3600)
    
    return response

@auth_router.get("/logout")
async def logout():
    response = Response(status_code=302)
    response.headers["Location"] = "/"
    response.delete_cookie(key="access_token")
    return response

# Dependência para extrair o usuário autenticado das requisições
def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado. Por favor, faça o login.")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Sessão expirada. Faça login novamente.")

@auth_router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    return user
