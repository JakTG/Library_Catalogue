import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import pandas as pd
import io
import numpy as np
import time

# Initialize session state to hold book data
if 'book_data' not in st.session_state:
    st.session_state.book_data = []

# Title and description
st.image("https://www.workspace-interiors.co.uk/application/files/thumbnails/xs/3416/1530/8285/tony_gee_large_logo_no_background.png", width=250)
st.title("Book OCR Extraction with Editable Catalogue")
st.write("Automated app to extract information from images using OCR, allowing users to compile everything into a catalogued library and download it as an Excel file.")

# How the app works expander
with st.expander("How to use the app"):
    st.write(
        """
        1. Upload up to 50 images of book covers or barcodes.
        2. Select the office location.
        3. The app extracts text from images using OCR.
        4. The extracted information is automatically catalogued.
        5. Click the 'Download Catalogue' button to save the catalog as an Excel file.
        """
    )

# Office selection drop-down
office = st.selectbox("Select Your Office", ["Manchester", "Esher", "Birmingham", "Stonehouse"])

# Image uploader (accepts up to 50 files)
uploaded_files = st.file_uploader("Choose up to 50 images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

# Clear session state when new images are uploaded
if uploaded_files:
    if 'last_uploaded_files' in st.session_state:
        if set(file.name for file in uploaded_files) != set(st.session_state.last_uploaded_files):
            st.session_state.book_data = []  # Reset catalog when new images are uploaded
    st.session_state.last_uploaded_files = [file.name for file in uploaded_files]

def preprocess_image(image):
    # Convert to grayscale
    image = image.convert('L')
    
    # Apply adaptive thresholding (binarization)
    image = ImageOps.autocontrast(image)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    
    # Sharpen image
    image = image.filter(ImageFilter.SHARPEN)
    
    return image

if uploaded_files:
    processed_files = set()
    for file in uploaded_files:
        if file.name in processed_files:
            continue  # Skip duplicate processing
        processed_files.add(file.name)
        
        image = Image.open(file)
        
        # Process image
        image_resized = image.resize((image.width // 2, image.height // 2))  # Reduce size to speed up processing
        image_preprocessed = preprocess_image(image_resized)
        
        # Perform OCR with optimized settings
        custom_config = "--psm 4 --oem 3"
        extracted_text = pytesseract.image_to_string(image_preprocessed, config=custom_config)
        
        # Extract non-empty lines
        lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
        
        # Assign extracted text to catalog fields
        title = lines[0] if len(lines) > 0 else "Unknown"
        edition = lines[1] if len(lines) > 1 else "N/A"
        author = lines[2] if len(lines) > 2 else "Unknown"
        
        # Convert image to byte format for embedding in DataFrame
        img_byte_arr = io.BytesIO()
        image.thumbnail((100, 100))  # Reduce image size for catalog display
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Append to session state book data
        new_entry = {"Image": img_byte_arr, "Title": title, "Edition": edition, "Author": author}
        st.session_state.book_data.append(new_entry)
    
    st.success("All images processed and added to the catalog!")

# Display the catalog with images
if st.session_state.book_data:
    st.subheader("Catalogue of Books")
    df_books = pd.DataFrame(st.session_state.book_data).drop_duplicates()
    st.session_state.book_data = df_books.to_dict("records")  # Ensure no duplicates persist
    
    # Convert images to displayable format
    def display_image(data):
        return f'<img src="data:image/png;base64,{data.encode("base64").decode()}" width="50">'
    
    df_books["Image"] = df_books["Image"].apply(display_image)
    st.markdown(df_books.to_html(escape=False), unsafe_allow_html=True)
    
    # Create Excel file and provide download button
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_books.to_excel(writer, index=False, sheet_name='Catalogue')
    output.seek(0)
    file_name = f"{office}_automated_catalogue.xlsx"
    st.download_button("Download Catalogue", output, file_name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
