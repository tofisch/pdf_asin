import io
import re
import zipfile
import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

def extract_asin_from_filename(filename: str) -> str | None:
    """Return ASIN found in the filename if present."""
    match = re.search(r"(B00[A-Za-z0-9]{7})", filename)
    return match.group(1) if match else ""

def create_overlay(text: str, page) -> io.BytesIO:
    """Create a PDF overlay with the given text for the size of the page."""
    packet = io.BytesIO()
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.drawString(width - 150, height - 30, text)
    can.save()
    packet.seek(0)
    return packet

def apply_text_to_pdf(pdf_bytes: bytes, text: str) -> io.BytesIO:
    """Add text to every page of the given PDF and return the modified PDF."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    prefix_text = f"ASIN: {text}"
    for page in reader.pages:
        overlay_packet = create_overlay(prefix_text, page)
        overlay_reader = PdfReader(overlay_packet)
        page.merge_page(overlay_reader.pages[0])
        writer.add_page(page)
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output

st.title("ASIN auf PDFs einfügen")

# Formular-Reset-Button
if st.button("Formular bereinigen"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

uploaded_files = st.file_uploader(
    "PDF Dateien hochladen (maximal 10)",
    type="pdf",
    accept_multiple_files=True,
    key="uploaded_files",
)

bulk_input = st.text_area(
    "ASINs im Bulk (eine ASIN pro Zeile)",
    key="bulk_input",
)

if uploaded_files:
    uploaded_files = uploaded_files[:10]  # Limit auf 10 Dateien
    bulk_asins = [line.strip() for line in bulk_input.splitlines() if line.strip()]
    asin_inputs = {}

    for idx, file in enumerate(uploaded_files):
        asin_key = f"asin_{idx}"

        # Reihenfolge: Bulk > Dateiname > Session State
        asin_from_filename = extract_asin_from_filename(file.name)
        asin_from_bulk = bulk_asins[idx] if idx < len(bulk_asins) else ""
        # Wenn kein Bulk, dann Filename, sonst Bulk
        suggested_asin = asin_from_bulk or asin_from_filename

        # Immer das Feld mit Dateinamen/ASIN initialisieren, wenn leer
        asin_value = st.session_state.get(asin_key, "")

        # Wenn Session State leer oder Datei wurde neu hochgeladen, dann initialisieren
        if not asin_value:
            asin_value = suggested_asin
            st.session_state[asin_key] = asin_value
        # Wenn Bulk überschrieben wird, aktualisiere Field
        elif asin_from_bulk and asin_value != asin_from_bulk:
            asin_value = asin_from_bulk
            st.session_state[asin_key] = asin_value
        # Wenn Datei neu hochgeladen wurde und Session State Wert passt nicht zum Filename, aktualisiere
        elif not asin_from_bulk and asin_from_filename and asin_value != asin_from_filename:
            asin_value = asin_from_filename
            st.session_state[asin_key] = asin_value

        asin_inputs[file.name] = st.text_input(
            label=f"ASIN für {file.name}",
            key=asin_key,
            value=asin_value,
        )

    if st.button("Alle einfügen"):
        if any(not st.session_state[f"asin_{idx}"].strip() for idx in range(len(uploaded_files))):
            st.error("Bitte alle Freitextfelder ausfüllen.")
        else:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for idx, file in enumerate(uploaded_files):
                    asin = st.session_state[f"asin_{idx}"]
                    processed = apply_text_to_pdf(file.getvalue(), asin)
                    zipf.writestr(file.name, processed.getvalue())
            zip_buffer.seek(0)
            st.success("Verarbeitung abgeschlossen.")
            st.download_button(
                label="Alle Dateien herunterladen",
                data=zip_buffer,
                file_name="asins.zip",
                mime="application/zip",
            )
else:
    st.info("Bitte lade bis zu 10 PDF-Dateien hoch.")
