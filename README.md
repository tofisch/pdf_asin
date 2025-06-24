# pdf_asin

Ein Streamlit-Tool, um bis zu zehn PDF-Dateien hochzuladen und auf jede Seite den Text
`ASIN: <Eingabe>` oben rechts einzufügen. Nach der Verarbeitung können alle Dateien
als ZIP heruntergeladen werden.

## Features

- Bis zu 10 PDF-Dateien gleichzeitig hochladen und verarbeiten
- Automatisches Auslesen einer ASIN (`B00*******`) aus dem Dateinamen (optional)
- Bulk-Eingabe von ASINs (eine pro Zeile, wird den PDFs der Reihe nach zugeordnet)
- Komfortable Bearbeitung der ASINs pro Datei im Interface
- Einfache Download-Funktion als ZIP-Archiv mit allen bearbeiteten PDFs

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
- Wird in einem Dateinamen bereits eine ASIN im Format `B00*******` erkannt, füllt
  das Tool das zugehörige Eingabefeld automatisch aus.
- Das Bulk-Feld erlaubt das Einfügen von bis zu zehn ASINs (eine pro Zeile),
  die in der Reihenfolge den PDFs zugeordnet werden.
- Nach der Bearbeitung stehen alle Dateien gesammelt als ZIP zum Download bereit.
