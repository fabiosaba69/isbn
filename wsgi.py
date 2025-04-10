"""
File wsgi.py - punto di ingresso per gunicorn
"""
# Importa app.py che carica tutte le route
from app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)