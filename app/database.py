import logging
from flask import Flask
from sqlalchemy import text
from app.models import db, Item, DeploymentLog

logger = logging.getLogger(__name__)

INITIAL_SEED_ITEMS = [
    {
        "title": "Heroku / Dokku / PaaS Ready",
        "description": "Configured with standard Procfile and runtime.txt for simple git-push-to-deploy platforms.",
        "category": "Cloud PaaS",
    },
    {
        "title": "Railway & Render Native",
        "description": "Native configuration with automatic environment variable injection and managed MySQL provisioning.",
        "category": "Cloud PaaS",
    },
    {
        "title": "Fly.io & Northflank MicroVMs",
        "description": "Configured with fly.toml and multi-region container orchestration.",
        "category": "Containers",
    },
    {
        "title": "Self-Hosted Systemd & Nginx",
        "description": "Hardened systemd unit file and production Nginx reverse proxy configuration for VPS or bare metal.",
        "category": "Self-Hosted",
    },
    {
        "title": "Cloudflare Tunnel (Zero Trust)",
        "description": "Expose homelab and local servers securely to the public internet without port forwarding or public IPs.",
        "category": "Networking",
    },
    {
        "title": "Tailscale Funnel & Serve",
        "description": "Point-to-point mesh network routing with automatic public HTTPS certificates via MagicDNS.",
        "category": "Networking",
    },
]


def seed_database_if_empty():
    """Checks if the database is empty and seeds initial demonstration items."""
    try:
        item_count = Item.query.count()
        if item_count == 0:
            logger.info("Database is empty. Seeding initial demonstration records...")
            for data in INITIAL_SEED_ITEMS:
                item = Item(
                    title=data["title"],
                    description=data["description"],
                    category=data["category"],
                )
                db.session.add(item)

            log_entry = DeploymentLog(
                event="DATABASE_INITIALIZED",
                details=f"Seeded {len(INITIAL_SEED_ITEMS)} initial demonstration items.",
            )
            db.session.add(log_entry)
            db.session.commit()
            logger.info(f"Database successfully seeded with {len(INITIAL_SEED_ITEMS)} items.")
            return True, f"Seeded {len(INITIAL_SEED_ITEMS)} items."
        return False, f"Database already contains {item_count} items."
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error seeding database: {e}")
        return False, str(e)


def initialize_database(app: Flask):
    """Initializes tables and seeds data within the application context."""
    with app.app_context():
        try:
            db.create_all()
            seeded, msg = seed_database_if_empty()
            logger.info(f"DB Init Status: {msg}")
        except Exception as e:
            # We log the warning but don't terminate the process, allows retrying on request
            logger.warning(
                f"Could not connect to database during startup (DB might still be initializing): {e}"
            )


def get_db_status():
    """Checks database health and returns latency and dialect info."""
    import time
    start = time.perf_counter()
    try:
        # Run a lightweight ping query
        db.session.execute(text("SELECT 1"))
        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        # Detect dialect & version
        dialect_name = db.engine.dialect.name
        try:
            version_res = db.session.execute(text("SELECT VERSION()")).scalar()
        except Exception:
            version_res = "Unknown"

        return {
            "connected": True,
            "latency_ms": latency_ms,
            "dialect": dialect_name,
            "version": version_res,
            "error": None,
        }
    except Exception as e:
        return {
            "connected": False,
            "latency_ms": None,
            "dialect": "Unknown",
            "version": None,
            "error": str(e),
        }
