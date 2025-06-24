import io
import re
import zipfile
import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import random

def extract_asin_from_filename(filename: str) -> str:
    # Exakt 10-stellige ASIN: B0XXXXXXXX
    match = re.search(r"B0[A-Za-z0-9]{8}", filename)
    return match.group(0) if match else ""

def create_overlay(text: str, page) -> io.BytesIO:
    packet = io.BytesIO()
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.drawString(width - 150, height - 30, text)
    can.save()
    packet.seek(0)
    return packet

def apply_text_to_pdf(pdf_bytes: bytes, text: str) -> io.BytesIO:
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

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = str(random.randint(1000, 1000000))

st.title("ASIN auf PDFs einfügen")

# PDFs löschen Button (setzt FileUploader-Key zurück)
if st.button("PDFs löschen"):
    st.session_state["uploader_key"] = str(random.randint(1000, 1000000))
    for key in list(st.session_state.keys()):
        if key.startswith("asin_"):
            del st.session_state[key]
    st.rerun()

uploaded_files = st.file_uploader(
    "PDF Dateien hochladen (maximal 10)",
    type="pdf",
    accept_multiple_files=True,
    key=st.session_state["uploader_key"],
)

if uploaded_files:
    uploaded_files = uploaded_files[:10]
    for idx, file in enumerate(uploaded_files):
        asin_key = f"asin_{idx}"
        asin_from_filename = extract_asin_from_filename(file.name)
        # Wenn Feld leer und ASIN im Dateinamen, automatisch übernehmen (aber nicht überschreiben)
        if asin_key not in st.session_state or not st.session_state[asin_key]:
            if asin_from_filename:
                st.session_state[asin_key] = asin_from_filename

        # Block: Dateiname, direkt darunter das Feld, dann Leerzeile
        st.markdown(f"{file.name}")  # Dateiname ohne Abstand
        st.text_input(
            label="",
            key=asin_key,
            value=st.session_state.get(asin_key, ""),
            max_chars=10,
            placeholder="ASIN",
        )
        st.markdown("")  # Leerzeile als Blocktrenner

    if st.button("Alle einfügen"):
        if any(not st.session_state.get(f"asin_{idx}", "").strip() for idx in range(len(uploaded_files))):
            st.error("Bitte alle Freitextfelder ausfüllen.")
        else:
            if len(uploaded_files) == 1:
                # Nur eine Datei -> Direkt als PDF zum Download anbieten
                file = uploaded_files[0]
                asin = st.session_state.get("asin_0", "")
                processed = apply_text_to_pdf(file.getvalue(), asin)
                st.success("Verarbeitung abgeschlossen.")
                st.download_button(
                    label="Datei herunterladen",
                    data=processed.getvalue(),
                    file_name=file.name,
                    mime="application/pdf",
                )
            else:
                # Mehrere Dateien -> ZIP anbieten
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zipf:
                    for idx, file in enumerate(uploaded_files):
                        asin = st.session_state.get(f"asin_{idx}", "")
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
