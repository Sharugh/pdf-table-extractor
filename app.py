import streamlit as st
import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import pandas as pd

# Set the path to tesseract if not installed globally (adjust path accordingly)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # for Windows

def extract_text_from_image(pdf_file):
    images = convert_from_path(pdf_file)  # Convert PDF to images
    text = ""
    
    # Perform OCR on each image and extract text
    for page_number, image in enumerate(images):
        text += pytesseract.image_to_string(image)
    
    return text

def extract_table_from_text(text):
    # Process the text and extract tabular data
    # This part depends on the structure of the text; use regex or manual parsing
    # For simplicity, you can attempt to convert the text into a DataFrame
    data = []
    lines = text.split('\n')
    
    for line in lines:
        columns = line.split()  # Adjust based on how the columns are separated
        if len(columns) > 1:
            data.append(columns)
    
    return pd.DataFrame(data)

def process_pdf(pdf_file):
    # Extract text using OCR
    text = extract_text_from_image(pdf_file)
    
    if not text:
        st.error(f"No text found in {pdf_file}. Please check if it's a valid scanned document.")
        return None
    
    # Extract table data
    df = extract_table_from_text(text)
    
    if df.empty:
        st.error(f"No table data found in {pdf_file}.")
        return None
    
    return df

def main():
    st.title("PDF Table Extractor using OCR")
    uploaded_files = st.file_uploader("Upload PDF Files", accept_multiple_files=True)
    
    if uploaded_files:
        all_dfs = []
        
        for uploaded_file in uploaded_files:
            st.write(f"Processing {uploaded_file.name}...")
            df = process_pdf(uploaded_file)
            if df is not None:
                all_dfs.append(df)
        
        # Combine all DataFrames into one Excel file and download
        if all_dfs:
            final_df = pd.concat(all_dfs, ignore_index=True)
            output_file = "extracted_data.xlsx"
            final_df.to_excel(output_file, index=False)
            st.success("Tables extracted successfully! Download your Excel file.")
            st.download_button("Download Excel", final_df.to_excel(index=False), file_name=output_file)

if __name__ == "__main__":
    main()
