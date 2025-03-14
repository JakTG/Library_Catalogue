import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import pandas as pd
import io

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

if uploaded_files:
    for file in uploaded_files:
        image = Image.open(file)
        
        # Enhance image for better OCR accuracy
        image = image.convert('L')  # Convert to grayscale
        image = image.filter(ImageFilter.SHARPEN)  # Apply sharpening filter
        enhancer = ImageEnhance.Contrast(image)
        enhanced_image = enhancer.enhance(2)  # Increase contrast
        
        # Perform OCR on the enhanced image
        extracted_text = pytesseract.image_to_string(enhanced_image, config='--psm 6')
        
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
