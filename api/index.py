# Vercel Serverless Function entry point
from wsgi import app

# Vercel requires exposing the WSGI/ASGI application as `app`
handler = app
