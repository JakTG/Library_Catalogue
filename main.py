# Packages used for the code
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import pandas as pd
import io

# --- Session State Init ---
if 'book_data' not in st.session_state:
    st.session_state.book_data = []

if 'processed_files' not in st.session_state:
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
        4. Editable table shown before exporting to Excel.
        5. Click 'Download Catalogue' to save it as an Excel file.
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
    accept_multiple_files=True
)

# Reset if new upload set
if uploaded_files:
    if "last_uploaded_files" in st.session_state:
        current_uploads = set(f.name for f in uploaded_files)
        if current_uploads != set(st.session_state.last_uploaded_files):
            st.session_state.book_data = []
            st.session_state.processed_files = set()
    st.session_state.last_uploaded_files = [f.name for f in uploaded_files]


# ======================================================
#   IMPROVED OCR & TEXT EXTRACTION FOR BOOK COVERS
# ======================================================

def preprocess_image(img):
    """Enhance image for much better OCR accuracy."""
    img = img.convert("L")  # grayscale
    img = ImageEnhance.Contrast(img).enhance(3)
    img = ImageEnhance.Sharpness(img).enhance(3)
    img = img.filter(ImageFilter.MedianFilter(size=3))  # small denoise

    # binarize
    img = img.point(lambda x: 0 if x < 140 else 255, "1")

    # upscale for OCR engine quality
    w, h = img.size
    img = img.resize((w * 2, h * 2))

    return img


def extract_book_info(text):
    """Extract Title, Author, Edition from OCR'd text."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    title = "Unknown"
    author = "Unknown"
    edition = "N/A"

    # edition detection
    for l in lines:
        if "edition" in l.lower():
            edition = l
            break

    # title = first strong line
    if len(lines) > 0:
        title = lines[0]

    # author detection
    for line in lines[1:]:
        lower = line.lower()

        # e.g. "By John Smith"
        if lower.startswith("by "):
            author = line[3:].strip()
            break

        # if line looks like a human name (alphabetic)
        if line.replace(" ", "").isalpha():
            author = line
            break

    return title, author, edition


def extract_book_data(file):
    """Full OCR pipeline for each book image."""
    img = Image.open(file)
    processed = preprocess_image(img)

    config = "--oem 3 --psm 6 -c preserve_interword_spaces=1"
    text = pytesseract.image_to_string(processed, config=config)

    title, author, edition = extract_book_info(text)

    return {
        "Image": file.name,
        "Title": title,
        "Author": author,
        "Edition": edition
    }


# ======================================================
#   PROCESS IMAGES (SAFE, NO THREADS)
# ======================================================

if uploaded_files:
    for file in uploaded_files:
        if file.name not in st.session_state.processed_files:
            with st.spinner(f"Processing {file.name}..."):
                result = extract_book_data(file)
                st.session_state.book_data.append(result)
                st.session_state.processed_files.add(file.name)

    st.success("All images processed!")


# ======================================================
#   DISPLAY TABLE + EXPORT
# ======================================================

if st.session_state.book_data:
    st.subheader("Editable Book Catalogue")

    df = pd.DataFrame(st.session_state.book_data).drop_duplicates()

    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    st.session_state.book_data = edited_df.to_dict("records")

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
