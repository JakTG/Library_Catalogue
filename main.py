import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import pandas as pd
import io

# --- Session State ---
if "book_data" not in st.session_state:
    st.session_state.book_data = []

if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

# --- UI ---
st.image("https://www.workspace-interiors.co.uk/application/files/thumbnails/xs/3416/1530/8285/tony_gee_large_logo_no_background.png", width=250)
st.title("Book OCR Extraction with Editable Catalogue")

office = st.selectbox("Select Your Office", ["Manchester", "Esher", "Birmingham", "Stonehouse"])

if st.button("🔄 Clear Catalogue"):
    st.session_state.book_data = []
    st.session_state.processed_files = set()

uploaded_files = st.file_uploader(
    "Upload images of all your books",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# --- Image Preprocessing ---
def preprocess_image(image):
    image = image.convert("L")
    image = ImageOps.autocontrast(image)
    image = ImageEnhance.Contrast(image).enhance(2)
    image = image.filter(ImageFilter.SHARPEN)

    max_width = 1000
    if image.width > max_width:
        ratio = max_width / float(image.width)
        image = image.resize((max_width, int(image.height * ratio)), Image.ANTIALIAS)

    return image

# --- OCR ---
def extract_book_data(file):
    image = Image.open(file)
    processed = preprocess_image(image)
    text = pytesseract.image_to_string(processed, config="--psm 6 --oem 3")

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return {
        "Image": file.name,
        "Title": lines[0] if len(lines) > 0 else "Unknown",
        "Edition": lines[1] if len(lines) > 1 else "N/A",
        "Author": lines[2] if len(lines) > 2 else "Unknown",
    }

# --- Process Files (SAFE, NO THREADS) ---
if uploaded_files:
    for file in uploaded_files:
        if file.name not in st.session_state.processed_files:
            with st.spinner(f"Processing {file.name}..."):
                result = extract_book_data(file)
                st.session_state.book_data.append(result)
                st.session_state.processed_files.add(file.name)

    st.success("All images processed!")

# --- Editable Table ---
if st.session_state.book_data:
    df = pd.DataFrame(st.session_state.book_data).drop_duplicates()
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    st.session_state.book_data = edited.to_dict("records")

    # Excel export
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        edited.to_excel(writer, index=False, sheet_name="Catalogue")
    output.seek(0)

    st.download_button(
        "Download Catalogue",
        output,
        f"{office}_automated_catalogue.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
