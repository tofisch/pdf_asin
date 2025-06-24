# pdf_asin

Ein Streamlit Tool, um bis zu zehn PDF-Dateien hochzuladen und auf jede Seite den Text
"ASIN: <Eingabe>" oben rechts einzufügen. Nach der Verarbeitung können alle Dateien
als ZIP heruntergeladen werden.

## Nutzung

1. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
2. Die Anwendung starten:
   ```bash
   streamlit run pdf_asin_app.py
   ```

Über die Oberfläche lassen sich die PDF-Dateien hochladen, die ASIN-Texte eingeben
und anschließend gesammelt herunterladen.
