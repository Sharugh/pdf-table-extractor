import os
import streamlit as st
import pytesseract
import pandas as pd
from pdf2image import convert_from_path
from PIL import Image

# Title of the App
st.title("PDF Table Extractor with OCR")
st.write("Upload scanned PDFs, and this app will extract tables into an Excel file.")

# File uploader
uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

# Tesseract configuration (local installation path)
# Update this path if needed (depends on your OS and where Tesseract is installed).
pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"  # Linux/Mac
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Windows

# Button to start processing
if st.button("Process PDFs"):
    if not uploaded_files:
        st.warning("Please upload at least one PDF.")
    else:
        output_path = "extracted_data.xlsx"
        all_data = {}

        # Loop through each uploaded PDF
        for uploaded_file in uploaded_files:
            pdf_name = uploaded_file.name
            st.write(f"Processing: {pdf_name}...")

            # Save the uploaded file temporarily
            with open(pdf_name, "wb") as f:
                f.write(uploaded_file.read())

            try:
                # Convert PDF to images
                st.write(f"Converting {pdf_name} to images...")
                images = convert_from_path(pdf_name, dpi=300)

                for page_num, image in enumerate(images, start=1):
                    # Perform OCR on the image
                    st.write(f"Performing OCR on Page {page_num} of {pdf_name}...")
                    text = pytesseract.image_to_string(image)

                    # Process text into rows and columns (simple table detection)
                    rows = [line.split() for line in text.split("\n") if line.strip()]
                    df = pd.DataFrame(rows)
                    all_data[f"{pdf_name}_Page_{page_num}"] = df

            except Exception as e:
                st.error(f"Error processing {pdf_name}: {e}")

            # Clean up the temporary file
            os.remove(pdf_name)

        # Save extracted data to an Excel file
        if all_data:
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                for sheet_name, df in all_data.items():
                    # Excel sheet names have a 31-character limit
                    sheet_name = sheet_name[:31]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            st.success("Data extraction complete!")
            # Provide a download button for the Excel file
            with open(output_path, "rb") as f:
                st.download_button(
                    label="Download Excel File",
                    data=f,
                    file_name="extracted_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
