import os
import streamlit as st
import pdfplumber
import pytesseract
from PIL import Image
import pandas as pd
import camelot

# Configure Tesseract for OCR (if needed)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # Adjust path as per your system

# Function to extract tables from PDFs
def extract_tables_from_pdf(pdf_path):
    tables = []
    try:
        extracted_tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")
        for table in extracted_tables:
            tables.append(table.df)
    except Exception as e:
        st.write(f"Skipping OCR Error: {e}")  # Ignores OCR errors
    return tables

# Streamlit App
st.title("📄 PDF Table Extractor")
st.write("Upload your PDF files containing tables and extract their data into a **single Excel sheet**.")

# File uploader
uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_tables = []  # To store all extracted tables
    output_path = "extracted_data.xlsx"

    for pdf_file in uploaded_files:
        st.write(f"🔄 Processing `{pdf_file.name}`...")

        # Save uploaded file temporarily
        temp_pdf_path = f"temp_{pdf_file.name}"
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())

        # Extract tables
        tables = extract_tables_from_pdf(temp_pdf_path)
        all_tables.extend(tables)

        # Remove the temporary file
        os.remove(temp_pdf_path)

    # Combine all extracted tables into a single DataFrame
    if all_tables:
        combined_df = pd.concat(all_tables, ignore_index=True)
        
        # Save everything in a **single sheet** in the Excel file
        combined_df.to_excel(output_path, index=False, sheet_name="Extracted_Tables")

        # Provide download link
        with open(output_path, "rb") as file:
            st.download_button(
                label="📥 Download Extracted Data",
                data=file,
                file_name="extracted_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
    else:
        st.error("⚠ No tables were extracted. Please check your PDF files!")
