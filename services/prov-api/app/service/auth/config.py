import os

JWT_ISSUER = os.getenv("JACQUES_JWT_ISSUER", "jacques.api")
JWT_ALGORITHM = "HS256"

JWT_SECRET = os.getenv("JACQUES_JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JACQUES_JWT_SECRET is not set")
