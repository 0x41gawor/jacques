# identity-api

```sh
POST /auth/google/login     (be daje fe link do okienka google::redirect, user otworzy to okienko i kliknie "Continue"
GET  /auth/google/callback  (tu google wyśle callback z google::redirect, to ostatecznie powinno zwrócić tokeny JWT)
POST /auth/refresh          (jak wygaśnie JWT::access-token to tutaj)
POST /auth/logout			(gdy fe chce wyczyścić refresh token to tutaj)
```
