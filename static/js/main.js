document.addEventListener('DOMContentLoaded', function() {
    // Inizializzazione di PDF.js
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.4.120/build/pdf.worker.min.js';
    
    // Elementi DOM
    const formInserimentoManuale = document.getElementById('formInserimentoManuale');
    const inputISBN = document.getElementById('inputISBN');
    const isbnFeedback = document.getElementById('isbnFeedback');
    const numISBN = document.getElementById('numISBN');
    const btnGeneraAuto = document.getElementById('btnGeneraAuto');
    const listaISBN = document.getElementById('listaISBN');
    const countISBN = document.getElementById('countISBN');
    const btnClearList = document.getElementById('btnClearList');
    const btnAggiungiSelezionati = document.getElementById('btnAggiungiSelezionati');
    const listaStampa = document.getElementById('listaStampa');
    const countStampa = document.getElementById('countStampa');
    const btnGeneraPDF = document.getElementById('btnGeneraPDF');
    const btnAnteprimaPDF = document.getElementById('btnAnteprimaPDF');
    const btnScaricaPDF = document.getElementById('btnScaricaPDF');
    const btnChiudiAnteprima = document.getElementById('btnChiudiAnteprima');
    const anteprimaContainer = document.getElementById('anteprima-container');
    const pdfViewer = document.getElementById('pdf-viewer');
    
    // Variabili di stato
    let isbnList = [];
    let isbnStampaList = [];
    let currentPDF = null;
    
    // Gestione dell'inserimento manuale di ISBN
    formInserimentoManuale.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const isbn = inputISBN.value.trim();
        
        // Validazione lato client semplice
        if (isbn.length < 10) {
            isbnFeedback.textContent = 'L\'ISBN deve essere di almeno 10 caratteri';
            isbnFeedback.className = 'form-text text-danger';
            return;
        }
        
        // Validazione server-side
        fetch('/valida-isbn', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `isbn=${encodeURIComponent(isbn)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.valido) {
                    isbnFeedback.textContent = data.messaggio;
                    isbnFeedback.className = 'form-text text-success';
                    
                    // Aggiungi ISBN alla lista
                    aggiungiIsbnAllaLista(isbn);
                    
                    // Pulisci l'input
                    inputISBN.value = '';
                } else {
                    isbnFeedback.textContent = data.messaggio;
                    isbnFeedback.className = 'form-text text-danger';
                }
            } else {
                isbnFeedback.textContent = 'Errore durante la validazione: ' + data.error;
                isbnFeedback.className = 'form-text text-danger';
            }
        })
        .catch(error => {
            isbnFeedback.textContent = 'Errore di connessione: ' + error;
            isbnFeedback.className = 'form-text text-danger';
        });
    });
    
    // Generazione automatica di ISBN
    btnGeneraAuto.addEventListener('click', function() {
        const quantity = parseInt(numISBN.value);
        
        if (quantity < 1 || quantity > 100) {
            alert('Inserisci un numero valido tra 1 e 100');
            return;
        }
        
        // Disabilita il pulsante durante la generazione
        btnGeneraAuto.disabled = true;
        btnGeneraAuto.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generazione...';
        
        // Funzione per generare un singolo ISBN
        const generaSingoloISBN = () => {
            return fetch('/genera-isbn', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    aggiungiIsbnAllaLista(data.isbn);
                } else {
                    console.error('Errore generazione ISBN:', data.error);
                }
            });
        };
        
        // Crea un array di promesse per generare tutti gli ISBN richiesti
        const promises = Array(quantity).fill().map(() => generaSingoloISBN());
        
        // Attendi il completamento di tutte le generazioni
        Promise.all(promises)
            .then(() => {
                // Ripristina il pulsante
                btnGeneraAuto.disabled = false;
                btnGeneraAuto.innerHTML = '<i class="fas fa-magic"></i> Genera';
            })
            .catch(error => {
                console.error('Errore durante la generazione:', error);
                btnGeneraAuto.disabled = false;
                btnGeneraAuto.innerHTML = '<i class="fas fa-magic"></i> Genera';
                alert('Si è verificato un errore durante la generazione degli ISBN');
            });
    });
    
    // Aggiunge un ISBN alla lista principale
    function aggiungiIsbnAllaLista(isbn) {
        // Verifica se è già presente
        if (isbnList.includes(isbn)) {
            isbnFeedback.textContent = 'Questo ISBN è già nella lista';
            isbnFeedback.className = 'form-text text-warning';
            return;
        }
        
        // Aggiungi alla lista
        isbnList.push(isbn);
        
        // Aggiorna la UI
        aggiornaListaIsbn();
    }
    
    // Aggiorna la visualizzazione della lista ISBN
    function aggiornaListaIsbn() {
        // Pulisci la lista
        listaISBN.innerHTML = '';
        
        // Aggiorna il contatore
        countISBN.textContent = isbnList.length;
        
        // Aggiorna lo stato dei pulsanti
        btnClearList.disabled = isbnList.length === 0;
        btnAggiungiSelezionati.disabled = isbnList.length === 0;
        
        // Aggiungi elementi alla lista
        isbnList.forEach((isbn, index) => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item';
            
            // Crea l'elemento per l'ISBN
            const isbnText = document.createElement('span');
            isbnText.textContent = isbn;
            
            // Crea il container per i pulsanti
            const buttonsContainer = document.createElement('div');
            
            // Crea il pulsante per l'anteprima del barcode
            const previewBtn = document.createElement('button');
            previewBtn.className = 'btn btn-sm btn-outline-secondary me-1';
            previewBtn.innerHTML = '<i class="fas fa-eye"></i>';
            previewBtn.title = 'Anteprima barcode';
            previewBtn.addEventListener('click', () => mostraAnteprimaBarcode(isbn));
            
            // Crea il pulsante per la rimozione
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn btn-sm btn-outline-danger';
            deleteBtn.innerHTML = '<i class="fas fa-times"></i>';
            deleteBtn.title = 'Rimuovi';
            deleteBtn.addEventListener('click', () => rimuoviIsbnDallaLista(index));
            
            // Aggiungi i pulsanti al container
            buttonsContainer.appendChild(previewBtn);
            buttonsContainer.appendChild(deleteBtn);
            
            // Aggiungi elementi al listItem
            listItem.appendChild(isbnText);
            listItem.appendChild(buttonsContainer);
            
            // Aggiungi alla lista
            listaISBN.appendChild(listItem);
        });
    }
    
    // Rimuove un ISBN dalla lista
    function rimuoviIsbnDallaLista(index) {
        isbnList.splice(index, 1);
        aggiornaListaIsbn();
    }
    
    // Mostra l'anteprima di un barcode
    function mostraAnteprimaBarcode(isbn) {
        fetch('/genera-barcode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `isbn=${encodeURIComponent(isbn)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Crea un modal per mostrare l'anteprima
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.id = 'barcodePreviewModal';
                modal.setAttribute('tabindex', '-1');
                modal.setAttribute('aria-hidden', 'true');
                
                modal.innerHTML = `
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Anteprima Barcode: ${isbn}</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Chiudi"></button>
                            </div>
                            <div class="modal-body text-center">
                                <img src="data:image/png;base64,${data.barcode}" alt="Barcode ${isbn}" class="img-fluid">
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Chiudi</button>
                            </div>
                        </div>
                    </div>
                `;
                
                // Aggiungi il modal al body
                document.body.appendChild(modal);
                
                // Inizializza e mostra il modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
                
                // Rimuovi il modal dal DOM quando viene chiuso
                modal.addEventListener('hidden.bs.modal', function() {
                    document.body.removeChild(modal);
                });
                
            } else {
                alert('Errore nella generazione del barcode: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Errore fetch:', error);
            alert('Errore di connessione durante la generazione del barcode');
        });
    }
    
    // Pulisci la lista ISBN
    btnClearList.addEventListener('click', function() {
        if (confirm('Sei sicuro di voler svuotare la lista?')) {
            isbnList = [];
            aggiornaListaIsbn();
        }
    });
    
    // Aggiungi alla lista di stampa
    btnAggiungiSelezionati.addEventListener('click', function() {
        if (isbnList.length === 0) return;
        
        // Aggiungi tutti gli ISBN alla lista di stampa
        isbnStampaList = [...isbnList];
        
        // Aggiorna l'interfaccia
        aggiornaListaStampa();
    });
    
    // Aggiorna la visualizzazione della lista di stampa
    function aggiornaListaStampa() {
        // Pulisci la lista
        listaStampa.innerHTML = '';
        
        // Aggiorna il contatore
        countStampa.textContent = isbnStampaList.length;
        
        // Aggiorna lo stato dei pulsanti
        btnGeneraPDF.disabled = isbnStampaList.length === 0;
        
        // Aggiungi elementi alla lista
        isbnStampaList.forEach((isbn, index) => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item';
            
            // Crea l'elemento per l'ISBN
            const isbnText = document.createElement('span');
            isbnText.textContent = isbn;
            
            // Crea il pulsante per la rimozione
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn btn-sm btn-outline-danger';
            deleteBtn.innerHTML = '<i class="fas fa-times"></i>';
            deleteBtn.title = 'Rimuovi';
            deleteBtn.addEventListener('click', () => rimuoviIsbnDallaListaStampa(index));
            
            // Aggiungi elementi al listItem
            listItem.appendChild(isbnText);
            listItem.appendChild(deleteBtn);
            
            // Aggiungi alla lista
            listaStampa.appendChild(listItem);
        });
    }
    
    // Rimuove un ISBN dalla lista di stampa
    function rimuoviIsbnDallaListaStampa(index) {
        isbnStampaList.splice(index, 1);
        aggiornaListaStampa();
    }
    
    // Genera il PDF
    btnGeneraPDF.addEventListener('click', function() {
        if (isbnStampaList.length === 0) return;
        
        // Ottieni le configurazioni
        const larghezza = document.getElementById('impostazioneLarghezza').value;
        const altezza = document.getElementById('impostazioneAltezza').value;
        const colonne = document.getElementById('impostazioneColonne').value;
        const righe = document.getElementById('impostazioneRighe').value;
        const mostraTesto = document.getElementById('mostraTestoCheck').checked;
        
        // Disabilita il pulsante durante l'elaborazione
        btnGeneraPDF.disabled = true;
        btnGeneraPDF.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generazione...';
        
        // Richiedi la generazione del PDF
        fetch('/genera-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                codici: isbnStampaList,
                larghezza: larghezza,
                altezza: altezza,
                colonne: colonne,
                righe: righe,
                mostraTesto: mostraTesto
            })
        })
        .then(response => response.json())
        .then(data => {
            // Ripristina il pulsante
            btnGeneraPDF.disabled = false;
            btnGeneraPDF.innerHTML = '<i class="fas fa-file-pdf me-1"></i> Genera PDF';
            
            if (data.success) {
                // Salva i dati del PDF per l'anteprima
                currentPDF = data.pdf_base64;
                
                // Abilita i pulsanti di anteprima e download
                btnAnteprimaPDF.disabled = false;
                btnScaricaPDF.disabled = false;
                
                // Mostra automaticamente l'anteprima
                mostraAnteprimaPDF();
            } else {
                alert('Errore nella generazione del PDF: ' + data.error);
            }
        })
        .catch(error => {
            btnGeneraPDF.disabled = false;
            btnGeneraPDF.innerHTML = '<i class="fas fa-file-pdf me-1"></i> Genera PDF';
            console.error('Errore fetch:', error);
            alert('Errore di connessione durante la generazione del PDF');
        });
    });
    
    // Mostra l'anteprima del PDF
    btnAnteprimaPDF.addEventListener('click', mostraAnteprimaPDF);
    
    function mostraAnteprimaPDF() {
        if (!currentPDF) return;
        
        // Mostra il container dell'anteprima
        anteprimaContainer.classList.remove('d-none');
        
        // Pulisci l'area di visualizzazione
        pdfViewer.innerHTML = '';
        
        // Carica il PDF da base64
        const pdfData = atob(currentPDF);
        const uint8Array = new Uint8Array(pdfData.length);
        for (let i = 0; i < pdfData.length; i++) {
            uint8Array[i] = pdfData.charCodeAt(i);
        }
        
        // Carica e renderizza il PDF
        pdfjsLib.getDocument({ data: uint8Array }).promise.then(pdfDoc => {
            const numPages = pdfDoc.numPages;
            
            // Renderizza ogni pagina
            for (let pageNum = 1; pageNum <= numPages; pageNum++) {
                pdfDoc.getPage(pageNum).then(page => {
                    const viewport = page.getViewport({ scale: 1.0 });
                    
                    // Crea un canvas per la pagina
                    const canvas = document.createElement('canvas');
                    canvas.className = 'pdf-canvas';
                    const context = canvas.getContext('2d');
                    
                    // Calcola la scala per adattare alla larghezza disponibile (80% del contenitore)
                    const containerWidth = pdfViewer.clientWidth * 0.8;
                    const scale = containerWidth / viewport.width;
                    const scaledViewport = page.getViewport({ scale });
                    
                    // Imposta le dimensioni del canvas
                    canvas.height = scaledViewport.height;
                    canvas.width = scaledViewport.width;
                    
                    // Aggiungi il canvas al contenitore
                    pdfViewer.appendChild(canvas);
                    
                    // Renderizza la pagina sul canvas
                    const renderContext = {
                        canvasContext: context,
                        viewport: scaledViewport
                    };
                    
                    page.render(renderContext);
                });
            }
        });
    }
    
    // Chiudi l'anteprima del PDF
    btnChiudiAnteprima.addEventListener('click', function() {
        anteprimaContainer.classList.add('d-none');
    });
    
    // Scarica il PDF
    btnScaricaPDF.addEventListener('click', function() {
        window.location.href = '/scarica-pdf';
    });
});
