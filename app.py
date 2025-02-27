import os
import streamlit as st
import pdfplumber
import pytesseract
from PIL import Image
import pandas as pd
import pdf2image

# Configure Tesseract OCR (Update if installed elsewhere)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\"

# Function to extract tables from digital PDFs using pdfplumber
def extract_tables_from_pdf(pdf_path):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_tables = page.extract_tables()
            for table in extracted_tables:
                tables.append(pd.DataFrame(table))
    return tables

# Function to extract tables from scanned PDFs (Images) using OCR
def extract_tables_from_images(pdf_path):
    tables = []
    images = pdf2image.convert_from_path(pdf_path)

    for img in images:
        ocr_text = pytesseract.image_to_string(img, config="--psm 6")
        lines = ocr_text.split("\n")
        table_data = [line.split() for line in lines if line.strip()]

        if table_data:
            df = pd.DataFrame(table_data)
            tables.append(df)

    return tables

# Streamlit App UI
st.title("📄 PDF Table Extractor")
st.write("Upload your PDF files (both **digital PDFs & scanned PDFs**) to extract tables into an **Excel sheet**.")

uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_tables = []
    output_path = "extracted_data.xlsx"

    for pdf_file in uploaded_files:
        st.write(f"🔄 Processing `{pdf_file.name}`...")

        temp_pdf_path = f"temp_{pdf_file.name}"
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())

        # Try extracting tables using pdfplumber (for digital PDFs)
        tables = extract_tables_from_pdf(temp_pdf_path)

        # If no tables found, use OCR for scanned PDFs
        if not tables:
            st.warning(f"⚠ No tables found using `pdfplumber`, trying OCR for `{pdf_file.name}`...")
            tables = extract_tables_from_images(temp_pdf_path)

        all_tables.extend(tables)
        os.remove(temp_pdf_path)

    if all_tables:
        combined_df = pd.concat(all_tables, ignore_index=True)
        combined_df.to_excel(output_path, index=False, sheet_name="Extracted_Tables")

        with open(output_path, "rb") as file:
            st.download_button(
                label="📥 Download Extracted Data",
                data=file,
                file_name="extracted_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
    else:
        st.error("⚠ No tables were extracted. Please check your PDF files!")

