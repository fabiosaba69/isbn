import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
# setup a secret key, required by sessions
app.secret_key = os.environ.get("SESSION_SECRET", "chiave_segreta_predefinita")
# configure the database, relative to the app instance folder
db_url = os.environ.get("DATABASE_URL")
if db_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    print(f"Database configurato con URL: {db_url}")
# initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401
    db.create_all()

# Registra le routes definite in app.py
from app import index, salva_isbn, elimina_isbn, genera_isbn, valida_isbn, genera_barcode, genera_pdf, scarica_pdf

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
