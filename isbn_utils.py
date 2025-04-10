import random
import io
import base64
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import isbnlib
from barcode.ean import EAN13
from barcode.writer import ImageWriter
from PIL import Image

def valida_isbn(isbn_str):
    """
    Valida un ISBN.
    Restituisce (True, "Valido") se valido, altrimenti (False, messaggio di errore)
    """
    # Rimuovi spazi e trattini
    isbn_str = isbn_str.replace(' ', '').replace('-', '')
    
    # Controllo lunghezza
    if len(isbn_str) not in [10, 13]:
        return False, "L'ISBN deve essere di 10 o 13 cifre"
    
    # Controlla se è numerico (o termina con X per ISBN-10)
    if not (isbn_str.isdigit() or (len(isbn_str) == 10 and isbn_str[:-1].isdigit() and isbn_str[-1] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X', 'x'])):
        return False, "L'ISBN deve contenere solo cifre (con possibile 'X' finale per ISBN-10)"
    
    # Verifica checksum con isbnlib
    try:
        if isbnlib.is_isbn10(isbn_str) or isbnlib.is_isbn13(isbn_str):
            return True, "ISBN valido"
        else:
            return False, "ISBN non valido: checksum errato"
    except Exception:
        return False, "Errore durante la validazione dell'ISBN"

def genera_isbn_casuale():
    """Genera un ISBN-13 casuale valido"""
    # Genera un prefisso EAN valido (978 o 979 per i libri)
    prefix = "978"
    
    # Gruppo linguistico (es. 88 per l'Italia)
    language_groups = ["88", "0", "1", "2", "3"]
    language = random.choice(language_groups)
    
    # Editore e titolo (lunghezza variabile)
    remaining_length = 9 - len(language)
    publisher_title = ''.join([str(random.randint(0, 9)) for _ in range(remaining_length)])
    
    # Combinati senza checksum (12 cifre)
    partial_isbn = prefix + language + publisher_title
    
    # Calcola il checksum manualmente
    check_digit = isbnlib.check_digit13(partial_isbn)
    full_isbn = partial_isbn + str(check_digit)
    
    # Formatta con trattini per leggibilità
    formatted_isbn = isbnlib.mask(full_isbn)
    return formatted_isbn

def genera_barcode_base64(isbn_str):
    """
    Genera un'immagine di codice a barre EAN-13 per l'ISBN fornito
    e restituiscila in formato base64
    """
    # Normalizza l'ISBN rimuovendo spazi e trattini
    isbn_str = isbn_str.replace(' ', '').replace('-', '')
    
    # Verifica che sia un ISBN valido
    if not (isbnlib.is_isbn10(isbn_str) or isbnlib.is_isbn13(isbn_str)):
        raise ValueError("ISBN non valido")
    
    # Converti ISBN-10 in ISBN-13 se necessario
    if len(isbn_str) == 10:
        check_digit = isbnlib.check_digit13("978" + isbn_str[:-1])
        isbn_str = "978" + isbn_str[:-1] + str(check_digit)
    
    # Genera il codice a barre (EAN13 accetta solo numeri)
    ean = EAN13(isbn_str, writer=ImageWriter())
    
    # Salva l'immagine in un buffer di memoria
    buffer = io.BytesIO()
    ean.write(buffer)
    
    # Resetta il puntatore del buffer
    buffer.seek(0)
    
    # Converti in base64
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_base64

def genera_pdf_barcode(codici, larghezza_mm, altezza_mm, colonne, righe, mostra_testo=True):
    """
    Genera un PDF A4 con i codici a barre specificati, disposti in una griglia
    
    Args:
        codici: lista di ISBN
        larghezza_mm: larghezza di ogni barcode in mm
        altezza_mm: altezza di ogni barcode in mm
        colonne: numero di colonne nella griglia
        righe: numero di righe nella griglia
        mostra_testo: se mostrare il testo ISBN sotto ogni barcode
    
    Returns:
        BytesIO: Buffer contenente il PDF generato
    """
    # Crea un buffer per il PDF
    buffer = io.BytesIO()
    
    # Crea il canvas PDF
    c = canvas.Canvas(buffer, pagesize=A4)
    larghezza_pagina, altezza_pagina = A4
    
    # Calcola i margini e lo spazio disponibile
    margine_mm = 10 * mm
    spazio_disponibile_larghezza = larghezza_pagina - 2 * margine_mm
    spazio_disponibile_altezza = altezza_pagina - 2 * margine_mm
    
    # Calcola lo spazio tra gli elementi
    spaziatura_x = spazio_disponibile_larghezza / colonne
    spaziatura_y = spazio_disponibile_altezza / righe
    
    # Converti le dimensioni in punti
    larghezza_pt = larghezza_mm * mm
    altezza_pt = altezza_mm * mm
    
    # Conta il numero di pagine necessarie
    codici_per_pagina = colonne * righe
    num_pagine = (len(codici) + codici_per_pagina - 1) // codici_per_pagina
    
    # Per ogni pagina
    for pagina in range(num_pagine):
        if pagina > 0:
            c.showPage()  # Nuova pagina
        
        idx_base = pagina * codici_per_pagina
        
        # Per ogni posizione nella griglia
        for i in range(righe):
            for j in range(colonne):
                idx = idx_base + i * colonne + j
                
                # Verifica se abbiamo ancora codici da elaborare
                if idx >= len(codici):
                    continue
                
                isbn = codici[idx].replace(' ', '').replace('-', '')
                
                # Converti ISBN-10 in ISBN-13 se necessario
                if len(isbn) == 10:
                    check_digit = isbnlib.check_digit13("978" + isbn[:-1])
                    isbn = "978" + isbn[:-1] + str(check_digit)
                
                # Genera il barcode come immagine
                ean = EAN13(isbn, writer=ImageWriter())
                buffer_img = io.BytesIO()
                ean.write(buffer_img)
                buffer_img.seek(0)
                
                # Apri l'immagine con PIL
                img = Image.open(buffer_img)
                
                # Calcola la posizione
                x = margine_mm + j * spaziatura_x + (spaziatura_x - larghezza_pt) / 2
                y = altezza_pagina - margine_mm - (i + 1) * spaziatura_y + (spaziatura_y - altezza_pt) / 2
                
                # Disegna il barcode
                c.drawInlineImage(img, x, y, width=larghezza_pt, height=altezza_pt)
                
                # Aggiungi il testo ISBN se richiesto
                if mostra_testo:
                    # Formatta l'ISBN per la leggibilità
                    isbn_formattato = isbnlib.mask(isbn)
                    c.setFont("Helvetica", 8)
                    testo_width = c.stringWidth(isbn_formattato, "Helvetica", 8)
                    c.drawString(
                        x + (larghezza_pt - testo_width) / 2,
                        y - 12,  # Spazio sotto il barcode
                        isbn_formattato
                    )
    
    # Finalizza il PDF
    c.save()
    buffer.seek(0)
    return buffer
