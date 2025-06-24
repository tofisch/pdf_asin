import io
import zipfile
import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas


def create_overlay(text: str, page) -> io.BytesIO:
    """Create a PDF overlay with the given text for the size of the page."""
    packet = io.BytesIO()
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    can = canvas.Canvas(packet, pagesize=(width, height))
    # Position near the top-right corner with some margin
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

uploaded_files = st.file_uploader(
    "PDF Dateien hochladen (maximal 10)",
    type="pdf",
    accept_multiple_files=True,
)

if uploaded_files:
    uploaded_files = uploaded_files[:10]  # Limit to 10 Dateien
    asin_inputs = {}
    for file in uploaded_files:
        asin_inputs[file.name] = st.text_input(
            label=f"ASIN für {file.name}",
            key=file.name,
        )

    if st.button("Alle einfügen"):
        if any(not value.strip() for value in asin_inputs.values()):
            st.error("Bitte alle Freitextfelder ausfüllen.")
        else:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zipf:
                for file in uploaded_files:
                    processed = apply_text_to_pdf(
                        file.getvalue(), asin_inputs[file.name]
                    )
                    zipf.writestr(file.name, processed.getvalue())
            zip_buffer.seek(0)
            st.success("Verarbeitung abgeschlossen.")
            st.download_button(
                label="Alle Dateien herunterladen",
                data=zip_buffer,
                file_name="asins.zip",
                mime="application/zip",
            )
