import os
import streamlit as st
import pdfplumber
import pytesseract
from PIL import Image
import pandas as pd
import camelot

# Configure Tesseract for OCR
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # Adjust path for your system

# Function to extract tables from PDFs
def extract_tables_from_pdf(pdf_path):
    tables = []
    try:
        extracted_tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")
        for table in extracted_tables:
            tables.append(table.df)
    except Exception as e:
        tables.append(pd.DataFrame([["Error extracting table:", str(e)]]))
    return tables

# Function to perform OCR on scanned PDFs
def perform_ocr_on_images(pdf_path):
    extracted_text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                if not page.extract_text():  # If no text is found
                    image = page.to_image()
                    ocr_text = pytesseract.image_to_string(image.original)
                    extracted_text.append(ocr_text)
    except Exception as e:
        extracted_text.append(f"Error performing OCR: {e}")
    return extracted_text

# Streamlit App
st.title("PDF Table Extractor")
st.write("Upload your PDF files containing tables (including scanned PDFs) and extract their data into an Excel file.")

# File uploader
uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_tables = []
    output_path = "extracted_data.xlsx"

    for pdf_file in uploaded_files:
        st.write(f"Processing {pdf_file.name}...")
        
        # Save uploaded file temporarily
        with open(pdf_file.name, "wb") as f:
            f.write(pdf_file.getbuffer())

        # Extract tables
        tables = extract_tables_from_pdf(pdf_file.name)
        all_tables.extend(tables)

        # Perform OCR for scanned PDFs (if needed)
        ocr_text = perform_ocr_on_images(pdf_file.name)
        if ocr_text:
            st.write(f"OCR text from {pdf_file.name}:")
            st.write("\n".join(ocr_text))

    # Combine all tables into a single Excel file
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for i, table in enumerate(all_tables):
            table.to_excel(writer, index=False, sheet_name=f"Table_{i + 1}")

    # Download link
    with open(output_path, "rb") as file:
        btn = st.download_button(
            label="Download Extracted Data",
            data=file,
            file_name="extracted_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
