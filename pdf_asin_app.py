import io
import re
import zipfile
import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import random

def extract_asin_from_filename(filename: str) -> str:
    matches = list(re.finditer(r"B0[A-Za-z0-9]{7}", filename))
    return matches[-1].group(0) if matches else ""

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
        if key.startswith("asin_") or key.startswith("asin_btn_"):
            del st.session_state[key]
    st.rerun()

uploaded_files = st.file_uploader(
    "PDF Dateien hochladen (maximal 10)",
    type="pdf",
    accept_multiple_files=True,
    key=st.session_state["uploader_key"],
)

# Formular-Reset-Button (bereinigt nur ASIN-Felder)
if st.button("Formular bereinigen"):
    for key in list(st.session_state.keys()):
        if key.startswith("asin_") or key.startswith("asin_btn_"):
            del st.session_state[key]
    st.rerun()

if uploaded_files:
    uploaded_files = uploaded_files[:10]

    # --- Button-Trigger-Mechanik ---
    # Prüfe: Wurde bei einem der Einträge ein Buttonklick getriggert? Dann setze den ASIN-Wert und lösche den Trigger.
    for idx, file in enumerate(uploaded_files):
        btn_key = f"asin_btn_{idx}"
        asin_key = f"asin_{idx}"
        asin_from_filename = extract_asin_from_filename(file.name)
        if st.session_state.get(btn_key, False):
            st.session_state[asin_key] = asin_from_filename
            st.session_state[btn_key] = False
            st.rerun()

    for idx, file in enumerate(uploaded_files):
        asin_key = f"asin_{idx}"
        btn_key = f"asin_btn_{idx}"
        asin_from_filename = extract_asin_from_filename(file.name)
        asin_value = st.session_state.get(asin_key, "")
        st.write(file.name)

        # 3-Spalten-Layout: [leer] [Textfeld] [Button]
        cols = st.columns([1, 2, 2, 1])
        asin_value_new = cols[1].text_input(
            label="",
            key=asin_key,
            value=asin_value,
            max_chars=20,
            placeholder="ASIN",
        )
        if asin_from_filename:
            if cols[2].button("ASIN aus Datei übernehmen", key=f"btn_{btn_key}"):
                st.session_state[btn_key] = True
                st.rerun()
        else:
            cols[2].markdown("&nbsp;", unsafe_allow_html=True)

    if st.button("Alle einfügen"):
        if any(not st.session_state.get(f"asin_{idx}", "").strip() for idx in range(len(uploaded_files))):
            st.error("Bitte alle Freitextfelder ausfüllen.")
        else:
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
