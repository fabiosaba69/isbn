from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from main import db

class ISBN(db.Model):
    """Modello per gli ISBN salvati nel database"""
    id = db.Column(db.Integer, primary_key=True)
    codice = db.Column(db.String(20), nullable=False, unique=True)
    descrizione = db.Column(db.String(200), nullable=True)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ISBN {self.codice}>'
    
    def to_dict(self):
        """Converte il modello in dizionario per JSON"""
        return {
            'id': self.id,
            'codice': self.codice,
            'descrizione': self.descrizione,
            'data_creazione': self.data_creazione.strftime('%d/%m/%Y %H:%M:%S')
        }