import os
import logging
import io
import base64
import uuid
import time
from flask import render_template, request, jsonify, send_file, session
from main import app, db
import isbn_utils
from models import ISBN

# Configurazione logging per debug
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    """Renderizza la pagina principale dell'applicazione"""
    # Ottieni gli ISBN salvati nel database
    isbn_salvati = ISBN.query.order_by(ISBN.data_creazione.desc()).all()
    return render_template('index.html', isbn_salvati=[isbn.to_dict() for isbn in isbn_salvati])

@app.route('/salva-isbn', methods=['POST'])
def salva_isbn():
    """Salva un ISBN nel database"""
    try:
        dati = request.get_json()
        codice = dati.get('isbn', '').replace(' ', '').replace('-', '')
        descrizione = dati.get('descrizione', '')
        
        # Verifica che l'ISBN sia valido
        valido, _ = isbn_utils.valida_isbn(codice)
        if not valido:
            return jsonify({'success': False, 'error': 'ISBN non valido'})
        
        # Verifica se l'ISBN esiste già
        if ISBN.query.filter_by(codice=codice).first():
            return jsonify({'success': False, 'error': 'ISBN già presente nel database'})
        
        # Crea un nuovo record
        nuovo_isbn = ISBN(codice=codice, descrizione=descrizione)
        db.session.add(nuovo_isbn)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'ISBN salvato con successo',
            'isbn': nuovo_isbn.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Errore durante il salvataggio dell'ISBN: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/elimina-isbn/<int:isbn_id>', methods=['DELETE'])
def elimina_isbn(isbn_id):
    """Elimina un ISBN dal database"""
    try:
        isbn = ISBN.query.get(isbn_id)
        if not isbn:
            return jsonify({'success': False, 'error': 'ISBN non trovato'})
        
        db.session.delete(isbn)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'ISBN eliminato con successo'})
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Errore durante l'eliminazione dell'ISBN: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/genera-isbn', methods=['POST'])
def genera_isbn():
    """Genera un ISBN casuale valido"""
    try:
        isbn = isbn_utils.genera_isbn_casuale()
        return jsonify({'success': True, 'isbn': isbn})
    except Exception as e:
        logging.error(f"Errore durante la generazione dell'ISBN: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/valida-isbn', methods=['POST'])
def valida_isbn():
    """Valida un ISBN inserito manualmente"""
    isbn = request.form.get('isbn', '')
    try:
        valido, messaggio = isbn_utils.valida_isbn(isbn)
        return jsonify({'success': True, 'valido': valido, 'messaggio': messaggio})
    except Exception as e:
        logging.error(f"Errore durante la validazione dell'ISBN: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/genera-barcode', methods=['POST'])
def genera_barcode():
    """Genera un'immagine di codice a barre per un ISBN"""
    isbn = request.form.get('isbn', '')
    try:
        immagine_base64 = isbn_utils.genera_barcode_base64(isbn)
        return jsonify({
            'success': True, 
            'barcode': immagine_base64
        })
    except Exception as e:
        logging.error(f"Errore durante la generazione del barcode: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/genera-pdf', methods=['POST'])
def genera_pdf():
    """Genera un file PDF con i codici a barre specificati"""
    try:
        dati = request.get_json()
        
        codici = dati.get('codici', [])
        larghezza = float(dati.get('larghezza', 50))
        altezza = float(dati.get('altezza', 30))
        colonne = int(dati.get('colonne', 2))
        righe = int(dati.get('righe', 4))
        mostra_testo = dati.get('mostraTesto', True)
        
        # Controllo dei parametri di input
        if not codici:
            return jsonify({'success': False, 'error': 'Nessun codice ISBN fornito'})
            
        if larghezza <= 0 or altezza <= 0:
            return jsonify({'success': False, 'error': 'Dimensioni non valide'})
            
        if colonne <= 0 or righe <= 0:
            return jsonify({'success': False, 'error': 'Layout non valido'})
        
        # Genera il PDF
        pdf_buffer = isbn_utils.genera_pdf_barcode(
            codici, larghezza, altezza, colonne, righe, mostra_testo
        )
        
        # Genera un ID univoco per il PDF
        pdf_id = str(uuid.uuid4())
        pdf_path = os.path.join('/tmp', f'pdf_{pdf_id}.pdf')
        
        # Salva il PDF su file system
        with open(pdf_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        # Memorizza il path in sessione
        session['ultimo_pdf_path'] = pdf_path
        session['pdf_creation_time'] = time.time()
        
        # Converti in base64 per l'anteprima
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
        
        # Pulisci i vecchi file PDF
        pulisci_pdf_temporanei()
        
        return jsonify({
            'success': True, 
            'pdf_base64': pdf_base64,
            'pdf_id': pdf_id
        })
        
    except Exception as e:
        logging.error(f"Errore durante la generazione del PDF: {str(e)}", exc_info=True)
        return jsonify({
            'success': False, 
            'error': 'Si è verificato un errore durante la generazione del PDF. ' + str(e)
        }), 500

def pulisci_pdf_temporanei():
    """Elimina i file PDF temporanei più vecchi di 1 ora"""
    try:
        for filename in os.listdir('/tmp'):
            if filename.startswith('pdf_') and filename.endswith('.pdf'):
                filepath = os.path.join('/tmp', filename)
                if time.time() - os.path.getctime(filepath) > 3600:  # 1 ora
                    os.remove(filepath)
    except Exception as e:
        logging.warning(f"Errore durante la pulizia dei PDF temporanei: {str(e)}")

@app.route('/scarica-pdf', methods=['GET'])
def scarica_pdf():
    """Scarica l'ultimo PDF generato"""
    try:
        if 'ultimo_pdf_path' not in session:
            return "Nessun PDF disponibile per il download", 404
            
        pdf_path = session['ultimo_pdf_path']
        
        if not os.path.exists(pdf_path):
            return "PDF non più disponibile", 404
            
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='codici_isbn.pdf'
        )
        
    except Exception as e:
        logging.error(f"Errore durante il download del PDF: {str(e)}")
        return "Si è verificato un errore durante il download", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
