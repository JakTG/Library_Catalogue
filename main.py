import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import pandas as pd
import io
import cv2
import numpy as np

# Initialize session state to hold book data
if 'book_data' not in st.session_state:
    st.session_state.book_data = []

# Title and description
st.image("https://www.workspace-interiors.co.uk/application/files/thumbnails/xs/3416/1530/8285/tony_gee_large_logo_no_background.png", width=250)
st.title("Book OCR Extraction with Editable Catalogue")
st.write("Automated app to extract information from images using OCR, allowing users to compile everything into a catalogued library and download it as a CSV file.")

# How the app works expander
with st.expander("How to use the app"):
    st.write(
        """
        1. Upload up to 50 images of book covers or barcodes.
        2. Select the office location.
        3. The app extracts text from images using OCR.
        4. The extracted information is automatically catalogued.
        5. Download the compiled catalog as a CSV file.
        """
    )

# Office selection drop-down
office = st.selectbox("Select Your Office", ["Manchester", "Esher", "Birmingham", "Stonehouse"])

# Image uploader (accepts up to 50 files)
uploaded_files = st.file_uploader("Choose up to 50 images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

def preprocess_image(image):
    # Convert to grayscale
    image = image.convert('L')
    
    # Convert to OpenCV format
    img_array = np.array(image)
    
    # Apply adaptive thresholding
    img_array = cv2.adaptiveThreshold(img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Convert back to PIL Image
    processed_image = Image.fromarray(img_array)
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(processed_image)
    processed_image = enhancer.enhance(3)
    
    # Sharpen image
    processed_image = processed_image.filter(ImageFilter.SHARPEN)
    
    return processed_image

if uploaded_files:
    for file in uploaded_files:
        image = Image.open(file)
        
        # Process image
        image = preprocess_image(image)
        
        # Perform OCR with optimized settings
        custom_config = "--psm 6 --oem 3"
        extracted_text = pytesseract.image_to_string(image, config=custom_config)
        
        # Extract non-empty lines
        lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
        
        # Assign extracted text to catalog fields
        title = lines[0] if len(lines) > 0 else "Unknown"
        edition = lines[1] if len(lines) > 1 else "N/A"
        author = lines[2] if len(lines) > 2 else "Unknown"
        
        # Append to session state book data
        new_entry = {"Image": file.name, "Title": title, "Edition": edition, "Author": author}
        st.session_state.book_data.append(new_entry)
    
    st.success("All images processed and added to the catalog!")

# Display the catalog if there is any data
if st.session_state.book_data:
    st.subheader("Catalogue of Books")
    df_books = pd.DataFrame(st.session_state.book_data)
    st.dataframe(df_books)

    # Process & Download Catalogue Button
    if st.button("Download Catalogue as CSV"):
        output = io.BytesIO()
        df_books.to_csv(output, index=False)
        output.seek(0)
        file_name = f"{office}_automated_catalogue.csv"
        st.download_button("Download Catalogue", output, file_name, "text/csv")
