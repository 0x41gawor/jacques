import os
import requests
from flask import Flask, request

from db.executor import PostgresExecutor

from auth.service import issue_auth_tokens
from db.api import get_db
from flask import jsonify

app = Flask(__name__)

GOOGLE_CLIENT_ID = os.getenv("OAUTH2_CLIENT_GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_GOOGLE_CLIENT_SECRET")
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
REDIRECT_URI = "http://zliczto.pl:5000/auth/google/callback"

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

def verify_id_token(id_token_str: str):
    request = google_requests.Request()

    idinfo = id_token.verify_oauth2_token(
        id_token_str,
        request,
        GOOGLE_CLIENT_ID,
    )

    # issuer check (czasem ręcznie)
    if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
        raise ValueError("Wrong issuer")

    return idinfo


def exchange_code_for_tokens(code: str):
    """
    Server-to-server exchange:
    authorization_code -> access_token + id_token
    """
    payload = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }

    response = requests.post(
        GOOGLE_TOKEN_URL,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )

    response.raise_for_status()
    return response.json()


@app.route("/auth/google/callback")
def google_callback():
    code = request.args.get("code")
    state = request.args.get("state")

    if not code or not state:
        return "Missing code or state", 400

    try:
        token_response = exchange_code_for_tokens(code)
    except Exception as e:
        print("ERROR during token exchange:", e)
        return "Token exchange failed", 500

    id_token_str = token_response.get("id_token")
    idinfo = {}
    if id_token_str:
        try:
            idinfo = verify_id_token(id_token_str)
        except Exception as e:
            print("ERROR during ID token verification:", e)
            return "ID token verification failed", 500

    from repo.users import UserRepository
    
    repo = UserRepository(db=PostgresExecutor())

    google_id = idinfo["sub"]
    name = idinfo.get("name")

    user = repo.find_by_google_id(google_id)
    if user:
        print(f"User already exists: {user}")
    else:
        print("Creating new user...")
        user = repo.create_user(google_id=google_id, name=name)
        print(f"Created user: {user}")

    db = get_db()

    tokens = issue_auth_tokens(
        user_id=str(user.id),  # UUID → str (JWT sub)
        db=db,
    )

    return jsonify(tokens), 200



if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )