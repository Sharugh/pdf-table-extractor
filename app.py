import os
import pandas as pd
import streamlit as st
from wand.image import Image
from PyPDF2 import PdfReader
from pytesseract import image_to_string, pytesseract
from io import BytesIO
from PIL import Image as PILImage

# Path to Tesseract OCR (update the path based on your system)
pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update for Windows users

# Streamlit app title
st.title("PDF Table Extractor with OCR")

# Upload multiple PDFs
uploaded_files = st.file_uploader("Upload PDF files (scanned or standard)", accept_multiple_files=True, type=["pdf"])

if uploaded_files:
    # Create a temporary directory for intermediate files
    temp_dir = "temp_images"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Initialize output Excel data
    excel_data = {}

    for uploaded_file in uploaded_files:
        try:
            st.write(f"Processing {uploaded_file.name}...")
            pdf_name = uploaded_file.name
            # Read the uploaded PDF
            pdf_reader = PdfReader(uploaded_file)

            # Loop through all pages in the PDF
            for page_num, page in enumerate(pdf_reader.pages):
                st.write(f"Processing page {page_num + 1} of {pdf_name}...")
                # Save the PDF page as an image using Wand
                with Image(blob=page.extract_text_as_bytes(), resolution=300) as img:
                    img_path = os.path.join(temp_dir, f"page_{page_num + 1}.jpg")
                    img.save(filename=img_path)

                # Perform OCR on the image using pytesseract
                with PILImage.open(img_path) as pil_img:
                    ocr_text = image_to_string(pil_img)

                # Convert OCR text to structured data
                st.write(f"OCR extracted text from page {page_num + 1}:")
                st.text(ocr_text)

                # Extract table data (naive approach, you may need custom parsing for specific table structures)
                table_data = [line.split() for line in ocr_text.split("\n") if line.strip()]
                df = pd.DataFrame(table_data)

                # Append to Excel data
                excel_data[f"{pdf_name}_page_{page_num + 1}"] = df

        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")

    # Export to Excel
    if excel_data:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for sheet_name, df in excel_data.items():
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)

        st.success("PDF data extracted successfully!")

        # Provide the Excel file for download
        st.download_button(
            label="Download Excel File",
            data=output.getvalue(),
            file_name="extracted_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Clean up temporary files
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)

else:
    st.info("Please upload PDF files to start processing.")

