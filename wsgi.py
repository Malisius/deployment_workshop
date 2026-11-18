from app import create_app

# WSGI application callable for Gunicorn, uWSGI, and serverless handlers
app = create_app()

if __name__ == "__main__":
    port = app.config.get("PORT", 5000)
    host = app.config.get("HOST", "0.0.0.0")
    app.run(host=host, port=port)
