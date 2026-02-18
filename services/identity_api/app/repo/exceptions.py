class UserAlreadyExists(Exception):
    def __init__(self, google_id: str):
        super().__init__(f"User with google_id={google_id!r} already exists")
        self.google_id = google_id