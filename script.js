function updateDetails() {
    let codice = document.getElementById("codice").value;

    if (!codice) {
        document.getElementById("details").style.display = "none";
        return;
    }

    fetch('/get_details', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ codice: codice })
    })
    .then(response => response.json())
    .then(data => {
        if (data.dettagli_text) {
            document.getElementById("details-content").value = data.dettagli_text;
            document.getElementById("details").style.display = "block";
        } else {
            document.getElementById("details-content").value = "Nessun dettaglio disponibile";
        }
    })
    .catch(error => {
        console.error("Errore nel caricamento dei dettagli:", error);
        document.getElementById("details-content").value = "Errore nel caricamento";
    });
}
