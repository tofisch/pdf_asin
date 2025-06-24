import io
import re
import zipfile
import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

def extract_asin_from_filename(filename: str) -> str | None:
    """Return ASIN found in the filename if present."""
    match = re.search(r"(B00[A-Za-z0-9]{7})", filename)
    return match.group(1) if match else None

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
    # Lösche alle relevanten Keys inkl. Dateien
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

        # Falls kein Wert im Session State, von Dateiname extrahieren (nur beim allerersten Anzeigen)
        if asin_key not in st.session_state:
            asin_from_filename = extract_asin_from_filename(file.name) or ""
            # Bulk-ASIN überschreibt, falls vorhanden
            asin_value = bulk_asins[idx] if idx < len(bulk_asins) else asin_from_filename
            st.session_state[asin_key] = asin_value
        else:
            # Bulk-ASIN überschreibt bei jeder Änderung
            if idx < len(bulk_asins):
                st.session_state[asin_key] = bulk_asins[idx]

        asin_inputs[file.name] = st.text_input(
            label=f"ASIN für {file.name}",
            key=asin_key,
            value=st.session_state[asin_key],
        )

    if st.button("Alle einfügen"):
        if any(not value.strip() for value in asin_inputs.values()):
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
