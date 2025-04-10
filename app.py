import os
import logging
import io
import base64
from flask import Flask, render_template, request, jsonify, send_file, session
import isbn_utils

# Configurazione logging per debug
logging.basicConfig(level=logging.DEBUG)

# Creazione dell'applicazione Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "chiave_segreta_predefinita")

@app.route('/')
def index():
    """Renderizza la pagina principale dell'applicazione"""
    return render_template('index.html')

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
        
        # Converti il buffer in base64 per l'anteprima
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
        
        # Memorizza il PDF in sessione per il download
        session['ultimo_pdf'] = pdf_buffer.getvalue()
        
        return jsonify({
            'success': True, 
            'pdf_base64': pdf_base64
        })
        
    except Exception as e:
        logging.error(f"Errore durante la generazione del PDF: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/scarica-pdf', methods=['GET'])
def scarica_pdf():
    """Scarica l'ultimo PDF generato"""
    try:
        if 'ultimo_pdf' not in session:
            return "Nessun PDF disponibile per il download", 404
            
        pdf_data = session['ultimo_pdf']
        return send_file(
            io.BytesIO(pdf_data),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='codici_isbn.pdf'
        )
        
    except Exception as e:
        logging.error(f"Errore durante il download del PDF: {str(e)}")
        return "Si è verificato un errore durante il download", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
