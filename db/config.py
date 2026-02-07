from dataclasses import dataclass
import os


@dataclass(frozen=True)
class PostgresConfig:
    user: str
    password: str
    host: str
    port: int
    dbname: str

    @classmethod
    def from_env(cls) -> "PostgresConfig":
        user = os.getenv("NOME")
        password = os.getenv("AGANDSKODE")
        port = os.getenv("THAREUX")
        host = os.getenv("DB_HOST", "localhost")

        if not all([user, password, port]):
            raise RuntimeError("NOME, AGANDSKODE and THAREUX must be set")

        return cls(
            user=user,
            password=password,
            host=host,
            port=int(port),
            dbname="jacques_db",
        )

    @property
    def dsn(self) -> str:
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.dbname}"
        )