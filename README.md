# pdf_asin

Ein Streamlit-Tool, um bis zu zehn PDF-Dateien hochzuladen und auf jede Seite den Text
`ASIN: <Eingabe>` oben rechts einzufügen. Nach der Verarbeitung können die Dateien
heruntergeladen werden – bei einer Datei direkt als PDF, ab zwei Dateien als ZIP.

## Features

- Bis zu 10 PDF-Dateien gleichzeitig hochladen und verarbeiten
- Automatisches Auslesen einer ASIN (`B0XXXXXXXX`) aus dem Dateinamen (sofern vorhanden, wird das Feld automatisch ausgefüllt)
- Komfortable Bearbeitung der ASINs pro Datei im Interface
- Einfache Download-Funktion:
  - Bei einer Datei: Direkt als PDF
  - Bei mehreren Dateien: ZIP-Archiv mit allen bearbeiteten PDFs

## Nutzung

1. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
2. Die Anwendung starten:
   ```bash
   streamlit run pdf_asin_app.py
   ```

### Hinweise

- Die ASIN kann pro Datei individuell angepasst werden.
- Wird in einem Dateinamen bereits eine ASIN im Format `B0XXXXXXXX` erkannt, füllt
  das Tool das zugehörige Eingabefeld automatisch aus.
- Nach der Bearbeitung steht entweder die einzelne Datei direkt als PDF oder alle Dateien gesammelt als ZIP zum Download bereit.
