# Packages that are being used in the app 
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import pandas as pd
import io
import numpy as np

# Initialize session state to hold book data- add a refresh button to clear the session
if 'book_data' not in st.session_state:
    st.session_state.book_data = []

# Title and description
st.image("https://www.workspace-interiors.co.uk/application/files/thumbnails/xs/3416/1530/8285/tony_gee_large_logo_no_background.png", width=250)
st.title("Book OCR Extraction with Editable Catalogue")
st.write("Automated app to extract information from images using OCR, allowing users to compile everything into a catalogued library and download it as an Excel file.")

# How the app works expander and how to use it
with st.expander("How to use the app"):
    st.write(
        """
        1. Upload all images of your books
        2. Select the office location.
        3. The app extracts text from images using OCR.
        4. The extracted information is automatically catalogued.
        5. Click the 'Download Catalogue' button to save the catalog as an Excel file.
        """
    )

# Office selection drop-down
office = st.selectbox("Select Your Office", ["Manchester", "Esher", "Birmingham", "Stonehouse"])

# Image uploader (accepts up to 50 files)
uploaded_files = st.file_uploader("Choose all your images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

# Clear session state when new images are uploaded
# Session state- maybe try and set it to so if you do leave the app or refresh the app it will clear the session
# Needs to change from when you uploaded a book the session will change
if uploaded_files:
    if 'last_uploaded_files' in st.session_state:
        if set(file.name for file in uploaded_files) != set(st.session_state.last_uploaded_files): # remove the last_ as this will be creating sessions on every last upload
            st.session_state.book_data = []  # Reset catalog when new images are uploaded, this resets the catalogue- remove this line to disregard the resetting of the catalogue
    st.session_state.last_uploaded_files = [file.name for file in uploaded_files]

def preprocess_image(image):
    # Convert to grayscale
    image = image.convert('L')
    
    # Enhance contrast and apply sharpening
    image = ImageOps.autocontrast(image)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
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
        image_preprocessed = preprocess_image(image)
        
        # Perform OCR with optimized settings- assuming a single column of text of variable sizes
        custom_config = "--psm 4 --oem 3"
        extracted_text = pytesseract.image_to_string(image_preprocessed, config=custom_config)
        
        # Extract non-empty lines
        lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
        
        # Assign extracted text to catalog fields
        title = lines[0] if len(lines) > 0 else "Unknown"
        edition = lines[1] if len(lines) > 1 else "N/A"
        author = lines[2] if len(lines) > 2 else "Unknown"

        # Code to alert the user if they are unable to read the image that was inputted
        # if edition == 'N/A' & title and author == 'Unknown:
        
        
        # Append to session state book data
        new_entry = {"Image": file, "Title": title, "Edition": edition, "Author": author}
        st.session_state.book_data.append(new_entry)
    
    st.success("All images processed and added to the catalog!")

# Display the catalog
if st.session_state.book_data:
    st.subheader("Catalogue of Books")
    df_books = pd.DataFrame(st.session_state.book_data).drop_duplicates()
    st.session_state.book_data = df_books.to_dict("records")  # Ensure no duplicates persist
    st.dataframe(df_books)
    
    # Create Excel file and provide download button
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_books.to_excel(writer, index=False, sheet_name='Catalogue')
    output.seek(0)
    file_name = f"{office}_automated_catalogue.xlsx"
    st.download_button("Download Catalogue", output, file_name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
