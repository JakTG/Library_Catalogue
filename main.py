import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import pandas as pd
import io

# Initialize session state to hold book data
if 'book_data' not in st.session_state:
    st.session_state.book_data = []

# Title and description
st.image("https://www.workspace-interiors.co.uk/application/files/thumbnails/xs/3416/1530/8285/tony_gee_large_logo_no_background.png", width=250)
st.title("Book OCR Extraction with Editable Catalogue")
st.write("Automated app to extract information from images using OCR, allowing users to compile everything into a catalogued library and download it as an Excel file.")

# How to use section
with st.expander("How to use the app"):
    st.write(
        """
        1. Upload 10+ images of your books.
        2. Select your office location.
        3. The app extracts text using OCR.
        4. You can edit the extracted data directly in the spreadsheet view.
        5. Click 'Download Catalogue' to save it as an Excel file.
        """
    )

# Office dropdown
office = st.selectbox("Select Your Office", ["Manchester", "Esher", "Birmingham", "Stonehouse"])

# Optional refresh button
if st.button("🔄 Clear Catalogue"):
    st.session_state.book_data = []

# Upload multiple images
uploaded_files = st.file_uploader(
    "Upload images of your books (10+ allowed)", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

# Reset book data if new images are uploaded
if uploaded_files:
    if 'last_uploaded_files' in st.session_state:
        if set(file.name for file in uploaded_files) != set(st.session_state.last_uploaded_files):
            st.session_state.book_data = []
    st.session_state.last_uploaded_files = [file.name for file in uploaded_files]

# Image preprocessing
def preprocess_image(image):
    image = image.convert('L')  # Grayscale
    image = ImageOps.autocontrast(image)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    image = image.filter(ImageFilter.SHARPEN)
    return image

# Process images if uploaded
if uploaded_files:
    processed_files = set(entry["Image"] for entry in st.session_state.book_data)

    for file in uploaded_files:
        if file.name in processed_files:
            continue

        image = Image.open(file)
        image_preprocessed = preprocess_image(image)

        # OCR config
        custom_config = "--psm 4 --oem 3"
        extracted_text = pytesseract.image_to_string(image_preprocessed, config=custom_config)

        lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
        title = lines[0] if len(lines) > 0 else "Unknown"
        edition = lines[1] if len(lines) > 1 else "N/A"
        author = lines[2] if len(lines) > 2 else "Unknown"

        # Append to session state
        st.session_state.book_data.append({
            "Image": file.name,
            "Title": title,
            "Edition": edition,
            "Author": author
        })

    st.success("Images processed and catalogued!")

# Show editable catalog
if st.session_state.book_data:
    st.subheader("📚 Editable Book Catalogue")

    df_books = pd.DataFrame(st.session_state.book_data).drop_duplicates()
    edited_df = st.data_editor(df_books, num_rows="dynamic", use_container_width=True)
    st.session_state.book_data = edited_df.to_dict("records")

    # Excel export
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        edited_df.to_excel(writer, index=False, sheet_name='Catalogue')
    output.seek(0)

    file_name = f"{office}_automated_catalogue.xlsx"
    st.download_button(
        "📥 Download Catalogue",
        output,
        file_name,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

