# JWT Patterns

Quick reference for JWT token implementation in KeyArc.

## Create Token
```python
from datetime import datetime, timedelta
from jose import jwt

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=2)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
```

## Validate Token
```python
from jose import JWTError, jwt
from fastapi import HTTPException

def validate_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(401, "Invalid token")
```

Remember: Short expiration (2 hours), include user_id in payload, validate on every request.
