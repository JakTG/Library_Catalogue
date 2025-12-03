# Packages used for the code
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import pandas as pd
import io

# --- Session State Init ---
if "book_data" not in st.session_state:
    st.session_state.book_data = []

if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

# --- UI Header ---
st.image(
    "https://www.workspace-interiors.co.uk/application/files/thumbnails/xs/3416/1530/8285/tony_gee_large_logo_no_background.png",
    width=250,
)
st.title("Book OCR Extraction with Editable Catalogue")
st.write(
    "Automated app to extract information from images using OCR, allowing users to compile everything into a "
    "catalogued library and download it as an Excel file."
)

with st.expander("How to use the app"):
    st.write(
        """
        1. Upload multiple images of your books.
        2. Select your office location.
        3. The app extracts text using OCR.
        4. Editable table appears before export.
        5. Click 'Download Catalogue' to save it.
        """
    )

# --- Office Selection ---
office = st.selectbox("Select Your Office", ["Manchester", "Esher", "Birmingham", "Stonehouse"])

# --- Clear Button ---
if st.button("🔄 Clear Catalogue"):
    st.session_state.book_data = []
    st.session_state.processed_files = set()

# --- Upload Images ---
uploaded_files = st.file_uploader(
    "Upload images of all your books",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
)

# Reset if a different set of files is uploaded
if uploaded_files:
    if "last_uploaded_files" in st.session_state:
        current_uploads = set(f.name for f in uploaded_files)
        if current_uploads != set(st.session_state.last_uploaded_files):
            st.session_state.book_data = []
            st.session_state.processed_files = set()
    st.session_state.last_uploaded_files = [f.name for f in uploaded_files]


# --- Improved OCR Preprocessing (no cv2) ---
def preprocess_image(img: Image.Image) -> Image.Image:
    # Grayscale
    img = img.convert("L")

    # Auto-contrast to stretch text contrast
    img = ImageOps.autocontrast(img)

    # Gentle contrast & sharpness (too strong can hurt)
    img = ImageEnhance.Contrast(img).enhance(1.8)
    img = ImageEnhance.Sharpness(img).enhance(1.5)

    # Light denoise
    img = img.filter(ImageFilter.MedianFilter(size=3))

    # Upscale if relatively small (helps OCR)
    target_width = 1000
    if img.width < target_width:
        scale = target_width / float(img.width)
        img = img.resize(
            (int(img.width * scale), int(img.height * scale)),
            Image.LANCZOS,
        )

    return img


# --- OCR Extraction: produce Line 1, Line 2, Line 3, ... ---
def extract_lines_for_file(file):
    img = Image.open(file)
    processed = preprocess_image(img)

    # OCR config tuned for block of text
    config = "--oem 3 --psm 6 -c preserve_interword_spaces=1"

    raw_text = pytesseract.image_to_string(processed, config=config)

    # Split into clean, non-empty lines
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    # Build row dict: Image, Line 1, Line 2, ...
    row = {"Image": file.name}
    for i, line in enumerate(lines):
        row[f"Line {i+1}"] = line

    return row


# --- Process Images ---
if uploaded_files:
    for file in uploaded_files:
        if file.name not in st.session_state.processed_files:
            with st.spinner(f"Processing {file.name}..."):
                row = extract_lines_for_file(file)
                st.session_state.book_data.append(row)
                st.session_state.processed_files.add(file.name)

    st.success("All images processed!")

# --- Editable Table ---
if st.session_state.book_data:
    st.subheader("Editable Book Catalogue")

    # DataFrame will have columns: Image, Line 1, Line 2, ...
    df_books = pd.DataFrame(st.session_state.book_data).drop_duplicates()
    edited_df = st.data_editor(df_books, num_rows="dynamic", use_container_width=True)
    st.session_state.book_data = edited_df.to_dict("records")

    # --- Excel Export ---
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        edited_df.to_excel(writer, index=False, sheet_name="Catalogue")
    output.seek(0)

    file_name = f"{office}_automated_catalogue.xlsx"
    st.download_button(
        "Download Catalogue",
        output,
        file_name,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
