function updateDetails() {
    let codice = document.getElementById("codice").value;

    if (!codice) {
        document.getElementById("details").style.display = "none";
        return;
    }

    console.log("🔄 Inviando richiesta per codice:", codice); // Debug in console

    fetch('/get_details', {  // ⚠️ Se usi Render, cambia con l'URL completo
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ codice: codice })
    })
    .then(response => response.json())
    .then(data => {
        console.log("✅ Risposta API ricevuta:", data); // Debug

        if (data.dettagli && typeof data.dettagli === 'object') {
            let dettagliText = "";
            for (let key in data.dettagli) {
                dettagliText += `${key}: ${data.dettagli[key]}\n`;
            }
            document.getElementById("details-content").value = dettagliText;
            document.getElementById("details").style.display = "block";
        } else {
            document.getElementById("details-content").value = "Nessun dettaglio disponibile";
        }
    })
    .catch(error => {
        console.error("❌ Errore nel caricamento dei dettagli:", error);
        document.getElementById("details-content").value = "Errore nel caricamento";
    });
}
