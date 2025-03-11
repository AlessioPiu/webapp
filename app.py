from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

# 🔹 Corretto: Assegniamo Flask solo una volta!
app = Flask(__name__, static_folder='static', template_folder='templates')

# Percorso del file Excel aggiornato
EXCEL_FILE = os.path.join(os.path.dirname(__file__), "dati.xlsx")
INTERVENTI_SHEET = "interventi"

# Funzione per leggere i dati degli impianti
def leggi_dati_excel():
    if not os.path.exists(EXCEL_FILE):
        print("❌ File Excel non trovato:", EXCEL_FILE)
        return []
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="impianti")
        df.columns = df.columns.str.strip()
        return df.to_dict(orient="records")
    except Exception as e:
        print("❌ Errore nel caricamento di Excel:", str(e))
        return []

@app.route("/", methods=["GET"])
def index():
    dati_impianti = leggi_dati_excel()
    return render_template('index.html', codici=[row["Codice Impianto"] for row in dati_impianti])

# ✅ API per ottenere i dettagli dell'impianto
@app.route('/get_details', methods=['POST'])
def get_details():
    print("🔄 Richiesta ricevuta su /get_details")
    dati_impianti = leggi_dati_excel()
    data = request.get_json()

    if not data or "codice" not in data:
        return jsonify({"error": "Codice impianto mancante"}), 400

    codice_selezionato = str(data["codice"])
    for row in dati_impianti:
        if str(row["Codice Impianto"]) == codice_selezionato:
            dettagli_text = "\n".join([f"{key}: {value}" for key, value in row.items()])
            return jsonify({"dettagli_text": dettagli_text})

    return jsonify({"dettagli_text": "Nessun dato trovato"})

# ✅ Configurazione per Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Avvio su porta {port}")
    app.run(debug=True, host='0.0.0.0', port=port)
