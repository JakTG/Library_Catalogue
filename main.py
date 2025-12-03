# Packages used for the code
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import time
import pytesseract
import pandas as pd
import io
import concurrent.futures

# --- Session State Init ---
if 'book_data' not in st.session_state:
    st.session_state.book_data = []

if 'processed_files' not in st.session_state:
    st.session_state.processed_files = set()

# --- UI Header ---
st.image("https://www.workspace-interiors.co.uk/application/files/thumbnails/xs/3416/1530/8285/tony_gee_large_logo_no_background.png", width=250)
st.title("Book OCR Extraction with Editable Catalogue")
st.write("Automated app to extract information from images using OCR, allowing users to compile everything into a catalogued library and download it as an Excel file.")

# Expander used to show how users can use the app
with st.expander("How to use the app"):
    st.write(
        """
        1. Upload multiple images of your books.
        2. Select your office location.
        3. The app extracts text using OCR.
        4. Editable table in the window view before exporting to excel file.
        5. Click 'Download Catalogue' to save it as an Excel file.
        """
    )

# --- Office Selection ---
office = st.selectbox("Select Your Office", ["Manchester", "Esher", "Birmingham", "Stonehouse"])

# --- Clear Button---
if st.button("🔄 Clear Catalogue"):
    st.session_state.book_data = []
    st.session_state.processed_files = set()

# --- Upload Images ---
uploaded_files = st.file_uploader(
    "Upload images of all your books",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# Uploading of files and being put into an Array
if uploaded_files:
    if 'last_uploaded_files' in st.session_state:
        current_uploads = set(file.name for file in uploaded_files)
        if current_uploads != set(st.session_state.last_uploaded_files):
            st.session_state.book_data = []
            st.session_state.processed_files = set()
    st.session_state.last_uploaded_files = [file.name for file in uploaded_files]

# --- Image Preprocessing ---
def preprocess_image(image):
    image = image.convert('L')
    image = ImageOps.autocontrast(image)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    image = image.filter(ImageFilter.SHARPEN)

    # Max width of a image that when added what it will go to
    max_width = 1000
    if image.width > max_width:
        ratio = max_width / float(image.width)
        new_height = int(float(image.height) * ratio)
        image = image.resize((max_width, new_height), Image.ANTIALIAS)

    return image

# --- OCR Processing Function ---
# NOTE: no use of st.session_state in this function anymore
def extract_book_data(file):
    image = Image.open(file)
    processed_img = preprocess_image(image)

    # Updated OCR config: --psm 6 = block of text
    custom_config = "--psm 6 --oem 3"
    text = pytesseract.image_to_string(processed_img, config=custom_config)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title = lines[0] if len(lines) > 0 else "Unknown"
    edition = lines[1] if len(lines) > 1 else "N/A"
    author = lines[2] if len(lines) > 2 else "Unknown"

    return {
        "Image": file.name,
        "Title": title,
        "Edition": edition,
        "Author": author
    }

# --- Process Images in Parallel ---
if uploaded_files:
    # Only process files we haven't seen before
    files_to_process = [
        f for f in uploaded_files
        if f.name not in st.session_state.processed_files
    ]

    if files_to_process:
        with st.spinner("Processing images..."):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = list(executor.map(extract_book_data, files_to_process))

            new_entries = [entry for entry in results if entry]
            st.session_state.book_data.extend(new_entries)

            # Update processed_files **after** threading
            st.session_state.processed_files.update(f.name for f in files_to_process)

        st.success("Images processed and catalogued!")
    else:
        st.info("All uploaded images have already been processed.")

# --- Editable Table View ---
if st.session_state.book_data:
    st.subheader("Editable Book Catalogue")

    # Any duplicates will be dropped from the dataframe
    df_books = pd.DataFrame(st.session_state.book_data).drop_duplicates()
    edited_df = st.data_editor(df_books, num_rows="dynamic", use_container_width=True)
    st.session_state.book_data = edited_df.to_dict("records")

    # --- Excel Export ---
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        edited_df.to_excel(writer, index=False, sheet_name='Catalogue')
    output.seek(0)

    # File name for the excel sheet when exporting the table
    file_name = f"{office}_automated_catalogue.xlsx"
    st.download_button(
        "Download Catalogue",
        output,
        file_name,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
