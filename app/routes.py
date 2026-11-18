import os
import platform
import socket
from datetime import datetime, timezone
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    current_app,
)
from app.models import db, Item, DeploymentLog
from app.database import get_db_status, seed_database_if_empty

main_bp = Blueprint("main", __name__)


def get_system_diagnostics():
    """Gathers system and runtime metadata."""
    return {
        "platform": current_app.config.get("PLATFORM", "Unknown"),
        "hostname": socket.gethostname(),
        "python_version": platform.python_version(),
        "os": f"{platform.system()} {platform.release()}",
        "port": current_app.config.get("PORT", 5000),
        "app_env": current_app.config.get("APP_ENV", "production"),
        "is_mysql": current_app.config.get("IS_MYSQL", False),
        "current_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }


@main_bp.route("/", methods=["GET"])
def index():
    """Main dashboard: displays database connectivity, items list, and creation form."""
    db_status = get_db_status()
    diagnostics = get_system_diagnostics()

    items = []
    item_count = 0
    if db_status["connected"]:
        try:
            items = Item.query.order_by(Item.created_at.desc()).all()
            item_count = len(items)
            # If connected but table is empty, auto-seed right away
            if item_count == 0:
                seeded, msg = seed_database_if_empty()
                if seeded:
                    flash(f"Auto-seeded database with sample records! ({msg})", "info")
                    items = Item.query.order_by(Item.created_at.desc()).all()
                    item_count = len(items)
        except Exception as e:
            flash(f"Error querying database: {e}", "danger")

    return render_template(
        "index.html",
        db_status=db_status,
        diagnostics=diagnostics,
        items=items,
        item_count=item_count,
    )


@main_bp.route("/items", methods=["POST"])
def add_item():
    """Create a new item via web form."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "General").strip()

    if not title:
        flash("Title is required.", "warning")
        return redirect(url_for("main.index"))

    try:
        new_item = Item(title=title, description=description, category=category)
        db.session.add(new_item)
        db.session.commit()
        flash(f"Item '{title}' successfully saved to MySQL database!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to save item: {e}", "danger")

    return redirect(url_for("main.index"))


@main_bp.route("/seed", methods=["POST"])
def seed_now():
    """Manual trigger to re-seed demo data if needed."""
    try:
        db.create_all()
        seeded, msg = seed_database_if_empty()
        if seeded:
            flash(f"Database seeded successfully: {msg}", "success")
        else:
            flash(f"Database already populated: {msg}", "info")
    except Exception as e:
        flash(f"Database initialization error: {e}", "danger")
    return redirect(url_for("main.index"))


# --------------------------------------------------------------------------
# API and Health Check Endpoints
# --------------------------------------------------------------------------

@main_bp.route("/healthz", methods=["GET"])
@main_bp.route("/health", methods=["GET"])
def health_check():
    """
    Standard cloud health check endpoint for liveness & readiness probes.
    (Render, Fly.io, Railway, Kubernetes, AWS ALB, etc.)
    """
    db_status = get_db_status()
    diagnostics = get_system_diagnostics()

    is_healthy = db_status["connected"]
    status_code = 200 if is_healthy else 503

    # Allow query parameter ?graceful=true to return 200 even if DB is still starting up
    if request.args.get("graceful", "false").lower() == "true":
        status_code = 200

    return jsonify({
        "status": "healthy" if is_healthy else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "diagnostics": diagnostics,
    }), status_code


@main_bp.route("/api/items", methods=["GET"])
def list_items_api():
    """REST API endpoint returning all items as JSON."""
    try:
        items = Item.query.order_by(Item.created_at.desc()).all()
        return jsonify({
            "status": "success",
            "count": len(items),
            "data": [item.to_dict() for item in items],
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@main_bp.route("/api/items", methods=["POST"])
def create_item_api():
    """REST API endpoint creating a new item from JSON."""
    payload = request.get_json(silent=True) or {}
    title = payload.get("title", "").strip()
    if not title:
        return jsonify({"status": "error", "message": "'title' field is required"}), 400

    try:
        item = Item(
            title=title,
            description=payload.get("description", ""),
            category=payload.get("category", "API"),
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({"status": "success", "data": item.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@main_bp.route("/api/info", methods=["GET"])
def info_api():
    """Diagnostics and platform inspection API endpoint."""
    return jsonify({
        "diagnostics": get_system_diagnostics(),
        "database": get_db_status(),
    }), 200
