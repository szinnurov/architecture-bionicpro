from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

app = FastAPI(title="Reports API", version="1.0.0")

KEYCLOAK_URL = "http://keycloak:8080"
REALM = "reports-realm"
CLIENT_ID = "reports-api"

public_keys_cache = None
public_keys_cache_time = None

security = HTTPBearer()

def get_public_keys():
    """Получение публичных ключей от Keycloak"""
    global public_keys_cache, public_keys_cache_time
    
    # Проверяем, не устарел ли кэш (обновляем каждые 5 минут)
    if (public_keys_cache is None or 
        public_keys_cache_time is None or 
        datetime.now() - public_keys_cache_time > timedelta(minutes=5)):
        
        try:
            response = requests.get(
                f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"
            )
            response.raise_for_status()
            public_keys_cache = response.json()
            public_keys_cache_time = datetime.now()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Не удалось получить публичные ключи: {str(e)}"
            )
    
    return public_keys_cache

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, key="", options={"verify_signature": False})
        
        import time
        current_time = time.time()
        if 'exp' in payload and payload['exp'] < current_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен истек"
            )
        
        return payload
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Недействительный токен: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Ошибка валидации токена: {str(e)}"
        )

def check_prothetic_user_role(payload: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    realm_access = payload.get('realm_access', {})
    roles = realm_access.get('roles', [])
    
    if 'prothetic_user' not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен. Требуется роль prothetic_user"
        )
    
    return payload

def generate_sample_report_data(user_id: str) -> Dict[str, Any]:
    return {
        "user_id": user_id,
        "report": "report mock"
    }

@app.get("/")
async def root():
    return {"message": "Reports API работает", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/reports", response_model=Dict[str, Any])
async def get_reports(payload: Dict[str, Any] = Depends(check_prothetic_user_role)):
    user_id = payload.get('sub', 'unknown')
    username = payload.get('preferred_username', 'unknown')
    
    report_data = generate_sample_report_data(user_id)
    
    return {
        "success": True,
        "message": f"Отчет для пользователя {username}",
        "data": report_data
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081) 
