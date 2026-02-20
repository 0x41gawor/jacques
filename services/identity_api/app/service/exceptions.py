# app/service/exceptions.py
class MissingOAuthCode(Exception):
    pass


class OAuthExchangeFailed(Exception):
    pass


class InvalidIdToken(Exception):
    pass

class InvalidRefreshToken(Exception):
    pass