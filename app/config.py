import os
import urllib.parse
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()


def detect_platform() -> str:
    """Detect the current deployment environment based on well-known platform env vars."""
    if os.environ.get("VERCEL"):
        return "Vercel Serverless"
    if os.environ.get("FLY_APP_NAME"):
        return f"Fly.io ({os.environ.get('FLY_REGION', 'global')})"
    if os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RAILWAY_PROJECT_ID"):
        return "Railway"
    if os.environ.get("RENDER"):
        return "Render"
    if os.environ.get("DYNO"):
        return "Heroku"
    if os.environ.get("NF_PROJECT_ID") or os.environ.get("NORTHFLANK"):
        return "Northflank"
    if os.environ.get("APP_PLATFORM_APP_ID"):
        return "DigitalOcean App Platform"
    if os.environ.get("KUBERNETES_SERVICE_HOST"):
        return "Kubernetes Cluster"
    if os.environ.get("AWS_EXECUTION_ENV") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return "AWS Lambda / App Runner"
    if os.environ.get("K_SERVICE"):
        return "Google Cloud Run"
    if os.path.exists("/.dockerenv") or os.environ.get("DOCKER_CONTAINER"):
        return "Docker Container (Self-Hosted)"
    return "Bare Metal / VPS / Local"


def build_database_uri() -> tuple[str, bool]:
    """
    Constructs the SQLAlchemy Database URI from multiple possible environment configurations.
    Returns (uri, is_mysql).
    """
    # 1. Check for consolidated Database URLs (standard in Heroku, Railway, Render, Fly)
    raw_url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("MYSQL_URL")
        or os.environ.get("JAWSDB_URL")
        or os.environ.get("CLEARDB_DATABASE_URL")
    )

    if raw_url:
        # Standardize MySQL schemes for SQLAlchemy + PyMySQL
        if raw_url.startswith("mysql://"):
            normalized_url = "mysql+pymysql://" + raw_url[len("mysql://"):]
            return normalized_url, True
        elif raw_url.startswith("mysql2://"):
            normalized_url = "mysql+pymysql://" + raw_url[len("mysql2://"):]
            return normalized_url, True
        elif raw_url.startswith("mysql+pymysql://"):
            return raw_url, True
        elif raw_url.startswith("postgres://") or raw_url.startswith("postgresql://"):
            # If a user provides postgres, adapt scheme for modern SQLAlchemy
            if raw_url.startswith("postgres://"):
                raw_url = "postgresql://" + raw_url[len("postgres://"):]
            return raw_url, False
        return raw_url, ("mysql" in raw_url)

    # 2. Check for individual MySQL environment variables
    mysql_host = os.environ.get("MYSQL_HOST")
    if mysql_host:
        user = urllib.parse.quote_plus(os.environ.get("MYSQL_USER", "root"))
        password = urllib.parse.quote_plus(os.environ.get("MYSQL_PASSWORD", ""))
        port = os.environ.get("MYSQL_PORT", "3306")
        dbname = os.environ.get("MYSQL_DATABASE", "deployment_workshop")

        # Optional SSL CA configuration (e.g. for PlanetScale, AWS RDS, Aiven)
        ssl_ca = os.environ.get("MYSQL_SSL_CA")
        ssl_params = ""
        if ssl_ca:
            ssl_params = f"?ssl_ca={urllib.parse.quote_plus(ssl_ca)}"

        uri = f"mysql+pymysql://{user}:{password}@{mysql_host}:{port}/{dbname}{ssl_params}"
        return uri, True

    # 3. Development Fallback to local SQLite if no MySQL config is detected
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    sqlite_path = os.path.join(base_dir, "deployment_workshop.db")
    return f"sqlite:///{sqlite_path}", False


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI, IS_MYSQL = build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Production-ready connection pooling
    # pool_pre_ping prevents 'MySQL server has gone away' after idle timeouts
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": int(os.environ.get("DB_POOL_RECYCLE", "280")),
    }

    # Port configuration (standard across Heroku, Railway, Render, Fly, Cloud Run)
    PORT = int(os.environ.get("PORT", "5000"))
    HOST = os.environ.get("HOST", "0.0.0.0")

    # Platform detection
    PLATFORM = detect_platform()
    APP_ENV = os.environ.get("FLASK_ENV", os.environ.get("APP_ENV", "production"))
