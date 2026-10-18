"""Configuracion de la aplicacion usando pydantic-settings.

Las variables de entorno se cargan de:
1. Variables de entorno del sistema
2. Archivo .env (si existe)

Prefijo: RMO_ (RickMortyOrders)
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracion de la aplicacion.

    Todos los valores pueden sobreescribirse con variables de entorno
    con prefijo RMO_ (ej: RMO_DATABASE_URL, RMO_API_URL, etc.)
    """

    model_config = SettingsConfigDict(
        env_prefix="RMO_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ============================================
    # Aplicacion
    # ============================================

    app_name: str = "Rick & Morty Orders"
    app_version: str = "0.1.0"
    environment: str = Field(default="development", pattern="^(development|staging|production)$")
    debug: bool = True

    # ============================================
    # API
    # ============================================

    host: str = "127.0.0.1"
    port: int = 8000

    # CORS: dominios permitidos (separados por coma)
    cors_origins: str = "*"

    # ============================================
    # Base de datos
    # ============================================

    # SQLite por defecto (para desarrollo)
    # En produccion: postgresql+psycopg://user:pass@host:5432/db
    database_url: str = "sqlite:///./rickmorty_orders.db"
    database_echo: bool = False

    # ============================================
    # Rick and Morty API
    # ============================================

    rickmorty_api_url: str = "https://rickandmortyapi.com/api"
    rickmorty_timeout: float = 10.0
    rickmorty_max_attempts: int = 3

    # ============================================
    # Seguridad (JWT - para futuro)
    # ============================================

    secret_key: str = "cambiar-en-produccion-usar-variable-de-entorno"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS origins como lista."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """True si estamos en produccion."""
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuracion (cacheada).

    Returns:
        Settings: instancia unica de la configuracion.
    """
    return Settings()
