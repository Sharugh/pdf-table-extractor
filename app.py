import os
import streamlit as st
import pdfplumber
import pytesseract
from PIL import Image
import pandas as pd
import camelot

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  

def extract_tables_from_pdf(pdf_path):
    tables = []
    try:
        extracted_tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")
        for table in extracted_tables:
            tables.append(table.df)
    except Exception as e:
        st.write(f"Skipping OCR Error: {e}") 
    return tables

st.title("📄 PDF Table Extractor")
st.write("Upload your PDF files containing tables and extract their data into a **single Excel sheet**.")

uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_tables = []  
    output_path = "extracted_data.xlsx"

    for pdf_file in uploaded_files:
        st.write(f"🔄 Processing `{pdf_file.name}`...")

        temp_pdf_path = f"temp_{pdf_file.name}"
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())

        tables = extract_tables_from_pdf(temp_pdf_path)
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
