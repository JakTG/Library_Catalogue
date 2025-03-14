import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import pandas as pd
import io

# Initialize session state to hold book data and current image index
if 'book_data' not in st.session_state:
    st.session_state.book_data = []
if 'current_image_index' not in st.session_state:
    st.session_state.current_image_index = 0

# Title and description
st.image("https://www.workspace-interiors.co.uk/application/files/thumbnails/xs/3416/1530/8285/tony_gee_large_logo_no_background.png", width=250)
st.title("Book OCR Extraction with Editable Catalogue")
st.write("Automated app to extract information from images using OCR, allowing users to correct fields and compile everything into a ready-made Excel file.")

# How the app works expander
with st.expander("How to use the app"):
    st.write(
        """
        1. Upload images of book covers or barcodes.
        2. Select the office location.
        3. The app extracts text from images using OCR.
        4. Review and edit extracted text if necessary.
        5. Move to the next image and repeat.
        6. Download the compiled catalog as an Excel file.
        """
    )

# Office selection drop-down
office = st.selectbox("Select Your Office", ["Manchester", "Esher", "Birmingham", "Stonehouse"])

# Image uploader (accepts multiple files)
uploaded_files = st.file_uploader("Choose images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    total_images = len(uploaded_files)
    current_index = st.session_state.current_image_index
    
    if current_index < total_images:
        file = uploaded_files[current_index]
        image = Image.open(file)
        
        # Enhance image for better OCR accuracy
        image = image.convert('L')  # Convert to grayscale
        image = image.filter(ImageFilter.SHARPEN)  # Apply sharpening filter
        enhancer = ImageEnhance.Contrast(image)
        enhanced_image = enhancer.enhance(2)  # Increase contrast
        
        # Display processed image
        st.image(enhanced_image, caption=f"Processed Image - {file.name}", width=200)
        
        # Perform OCR on the enhanced image
        extracted_text = pytesseract.image_to_string(enhanced_image, config='--psm 6')
        
        st.subheader("OCR Extracted Text")
        st.text(extracted_text)
        
        # Allow user to edit the extracted text
        corrected_text = st.text_area(f"Edit extracted text for {file.name}", value=extracted_text, height=150)
        
        # Extract non-empty lines
        lines = [line.strip() for line in corrected_text.splitlines() if line.strip()]
        
        if lines:
            st.subheader("Select the Appropriate Fields")
            title = st.selectbox("Select the Title", lines, index=0, key=f"title_{file.name}")
            edition_options = ["N/A"] + lines
            edition = st.selectbox("Select the Edition", edition_options, index=0, key=f"edition_{file.name}")
            author = st.selectbox("Select the Author", lines, index=len(lines)-1, key=f"author_{file.name}")
            
            if st.button("Add Book Data"):
                new_entry = {"Image": file.name, "Title": title, "Edition": edition, "Author": author}
                st.session_state.book_data.append(new_entry)
                st.success(f"Book data for {file.name} added to the table!")
                
                # Move to next image
                st.session_state.current_image_index += 1
                st.experimental_rerun()

# Display the editable table if there is any data
if st.session_state.book_data:
    st.subheader("Catalogue of Books")
    df_books = pd.DataFrame(st.session_state.book_data)
    edited_df = st.data_editor(df_books, num_rows="dynamic", key="data_editor")
    st.session_state.book_data = edited_df.to_dict("records")

# Process & Download Catalogue Button
if st.session_state.book_data:
    if st.button("Process & Download Catalogue"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame(st.session_state.book_data).to_excel(writer, index=False, sheet_name='Catalogue')
        excel_data = output.getvalue()
        file_name = f"{office}_automated_catalogue.xlsx"
        st.download_button("Download Catalogue", excel_data, file_name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
