from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Percorso del file Excel aggiornato
EXCEL_FILE = "C:/Users/alessio.piu/Desktop/app/dati.xlsx"
INTERVENTI_SHEET = "interventi"

# Funzione per leggere i dati degli impianti
def leggi_dati_excel():
    if not os.path.exists(EXCEL_FILE):
        print("File Excel non trovato!", EXCEL_FILE)
        return []
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name="impianti")
        df.columns = df.columns.str.strip()
        return df.to_dict(orient="records")
    except Exception as e:
        print("Errore nel caricamento di Excel:", str(e))
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
        print("Errore nel caricamento dei tecnici:", str(e))
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
        print("Errore nel caricamento degli interventi:", str(e))
        return []

@app.route("/", methods=["GET"])
def index():
    dati_impianti = leggi_dati_excel()
    tecnici = leggi_tecnici_excel()
    interventi = leggi_interventi_excel()
    
    codici_impianto = sorted(set(str(row["Codice Impianto"]) for row in dati_impianti))
    
    return render_template('index.html', codici=codici_impianto, tecnici=tecnici, interventi=interventi)

@app.route('/get_details', methods=['POST'])
def get_details():
    dati_impianti = leggi_dati_excel()
    data = request.json
    codice_selezionato = data.get("codice")

    for row in dati_impianti:
        if row["Codice Impianto"] == codice_selezionato:
            dettagli = {key: row[key] for key in row.keys()}
            dettagli_text = "\n".join([f"{key}: {value}" for key, value in dettagli.items()])
            return jsonify({"dettagli_text": dettagli_text})

    return jsonify({"dettagli_text": "Nessun dato trovato"})

@app.route('/salva_intervento', methods=['POST'])
def salva_intervento():
    data = request.json
    codice = data.get("codice")
    tecnico = data.get("tecnico")
    data_intervento = data.get("data_intervento")
    note = data.get("note")

    if not all([codice, tecnico, data_intervento, note]):
        return jsonify({"status": "error", "message": "Compila tutti i campi!"})

    nuovo_intervento = pd.DataFrame([{
        "Codice Impianto": codice,
        "Tecnico": tecnico,
        "Data Intervento": data_intervento,
        "Note": note
    }])

    try:
        with pd.ExcelWriter(EXCEL_FILE, mode="a", if_sheet_exists="replace") as writer:
            df_esistente = pd.read_excel(EXCEL_FILE, sheet_name=INTERVENTI_SHEET) if os.path.exists(EXCEL_FILE) else pd.DataFrame()
            df_finale = pd.concat([df_esistente, nuovo_intervento], ignore_index=True)
            df_finale.to_excel(writer, sheet_name=INTERVENTI_SHEET, index=False)
        return jsonify({"status": "success", "message": "Intervento salvato con successo!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Errore nel salvataggio: {str(e)}"})

@app.route('/interventi', methods=['GET'])
def interventi():
    interventi = leggi_interventi_excel()
    return render_template('interventi.html', interventi=interventi)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
