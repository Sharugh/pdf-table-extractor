import os
import pandas as pd
import streamlit as st
import pdfplumber
import pytesseract
from PIL import Image

# Configure Tesseract OCR (Optional, for local testing)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # Update path as needed

# Function to extract tables and OCR text from a PDF
def extract_data_from_pdf(pdf_path):
    extracted_data = pd.DataFrame()

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Extract tables
                tables = page.extract_tables()
                for table in tables:
                    df = pd.DataFrame(table[1:], columns=table[0])  # First row as header
                    extracted_data = pd.concat([extracted_data, df], ignore_index=True)
                
                # OCR for scanned images
                if not tables:
                    st.warning(f"No tables detected on page {page.page_number}. Attempting OCR.")
                    img = page.to_image()
                    text = pytesseract.image_to_string(img)
                    st.text(f"OCR text from page {page.page_number}:\n{text}")
    except Exception as e:
        st.error(f"Error processing {pdf_path}: {str(e)}")

    return extracted_data

# Streamlit app
st.title("PDF Table & OCR Extractor")
uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    output_path = "extracted_data.xlsx"
    final_data = pd.DataFrame()

    for pdf_file in uploaded_files:
        st.info(f"Processing {pdf_file.name}...")
        pdf_path = f"/tmp/{pdf_file.name}"
        with open(pdf_path, "wb") as f:
            f.write(pdf_file.read())

        data = extract_data_from_pdf(pdf_path)
        if not data.empty:
            final_data = pd.concat([final_data, data], ignore_index=True)

    if not final_data.empty:
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            final_data.to_excel(writer, index=False, sheet_name="Extracted Data")
        st.success(f"Excel file created: {output_path}")
        st.download_button("Download Excel File", data=open(output_path, "rb").read(), file_name="extracted_data.xlsx")
    else:
        st.error("No data extracted from the uploaded PDFs.")
