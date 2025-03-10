from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

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

# Funzione per leggere i tecnici
def leggi_tecnici_excel():
    if not os.path.exists(EXCEL_FILE):
        return []
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="tecnici")
        df.columns = df.columns.str.strip()
        return df["Nome Tecnico"].dropna().unique().tolist()
    except Exception as e:
        print("❌ Errore nel caricamento dei tecnici:", str(e))
        return []

# Funzione per leggere gli interventi salvati
def leggi_interventi_excel():
    if not os.path.exists(EXCEL_FILE):
        return []
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=INTERVENTI_SHEET)
        df.columns = df.columns.str.strip()
        return df.to_dict(orient="records")
    except Exception as e:
        print("❌ Errore nel caricamento degli interventi:", str(e))
        return []

@app.route("/", methods=["GET"])
def index():
    dati_impianti = leggi_dati_excel()
    tecnici = leggi_tecnici_excel()
    interventi = leggi_interventi_excel()
    
    codici_impianto = sorted(set(str(row["Codice Impianto"]) for row in dati_impianti))
    
    return render_template('index.html', codici=codici_impianto, tecnici=tecnici, interventi=interventi)

# ✅ CORRETTA DEFINIZIONE DELL'API `/get_details`
@app.route('/get_details', methods=['POST'])
def get_details():
    print("🔄 Richiesta ricevuta su /get_details")

    dati_impianti = leggi_dati_excel()
    data = request.get_json()

    if not data or "codice" not in data:
        print("⚠️ Richiesta non valida: manca il codice impianto")
        return jsonify({"error": "Codice impianto mancante"}), 400

    codice_selezionato = data["codice"]
    print(f"🔍 Ricerca dettagli per impianto: {codice_selezionato}")

    for row in dati_impianti:
        if str(row["Codice Impianto"]) == str(codice_selezionato):
            dettagli_text = "\n".join([f"{key}: {value}" for key, value in row.items()])
            return jsonify({"dettagli_text": dettagli_text})

    print("⚠️ Nessun impianto trovato con codice:", codice_selezionato)
    return jsonify({"dettagli_text": "Nessun dato trovato"})

@app.route('/salva_intervento', methods=['POST'])
def salva_intervento():
    data = request.get_json()
    
    if not data or not all(k in data for k in ["codice", "tecnico", "data_intervento", "note"]):
        return jsonify({"status": "error", "message": "Compila tutti i campi!"}), 400

    nuovo_intervento = pd.DataFrame([{
        "Codice Impianto": data["codice"],
        "Tecnico": data["tecnico"],
        "Data Intervento": data["data_intervento"],
        "Note": data["note"]
    }])

    try:
        with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace") as writer:
            df_esistente = pd.read_excel(EXCEL_FILE, sheet_name=INTERVENTI_SHEET) if os.path.exists(EXCEL_FILE) else pd.DataFrame()
            df_finale = pd.concat([df_esistente, nuovo_intervento], ignore_index=True)
            df_finale.to_excel(writer, sheet_name=INTERVENTI_SHEET, index=False)
        return jsonify({"status": "success", "message": "Intervento salvato con successo!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Errore nel salvataggio: {str(e)}"}), 500

@app.route('/interventi', methods=['GET'])
def interventi():
    interventi = leggi_interventi_excel()
    return render_template('interventi.html', interventi=interventi)

# ✅ CORRETTA CONFIGURAZIONE PER DEPLOY SU RENDER
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Render usa spesso 10000
    print(f"🚀 Avvio su porta {port}")
    app.run(debug=True, host='0.0.0.0', port=port)
