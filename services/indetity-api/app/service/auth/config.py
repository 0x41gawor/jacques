# auth/config.py
import os

JWT_ISSUER = "jacques.api"
JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_TTL_SECONDS = 15 * 60          # [s] 15 min
REFRESH_TOKEN_TTL_SECONDS = 30 * 24 * 3600  # [s] 30 dni

JWT_SECRET = os.getenv("JACQUES_JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JACQUES_JWT_SECRET is not set")

REFRESH_TOKEN_PEPPER = os.getenv("JACQUES_REFRESH_TOKEN_PEPPER")
if not REFRESH_TOKEN_PEPPER:
    raise RuntimeError("JACQUES_REFRESH_TOKEN_PEPPER is not set")