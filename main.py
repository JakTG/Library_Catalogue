# Packages used for the code
import streamlit as st
from PIL import Image
import pandas as pd
import io
from openpyxl.drawing.image import Image as XLImage  # for embedding images into Excel

# --- DEMO CONSTANTS (change these later if needed) ---
DEMO_TITLE = "Jak Snape"
DEMO_EDITION = "1421943"   # Sentinel number
DEMO_AUTHOR = "1"          # Issue number

# --- Session State Init ---
if "book_data" not in st.session_state:
    st.session_state.book_data = []

if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

# store image bytes so we can embed them into Excel
if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = {}

# --- UI Header ---
st.image(
    "https://www.workspace-interiors.co.uk/application/files/thumbnails/xs/3416/1530/8285/tony_gee_large_logo_no_background.png",
    width=250,
)
st.title("Book OCR Extraction with Editable Catalogue")
st.write(
    "Automated app to extract information from images (demo currently using fixed values) "
    "and compile everything into a catalogued library that can be downloaded as an Excel file."
)

with st.expander("How to use the app"):
    st.write(
        """
        1. Upload multiple images of your books (or demo images).
        2. Select your office location.
        3. The app fills in demo data for Title / Edition / Author.
        4. You can edit the table before exporting to Excel.
        5. Click 'Download Catalogue' to save it as an Excel file (with images embedded).
        """
    )

# --- Office Selection ---
office = st.selectbox("Select Your Office", ["Manchester", "Esher", "Birmingham", "Stonehouse"])

# --- Clear Button ---
if st.button("🔄 Clear Catalogue"):
    st.session_state.book_data = []
    st.session_state.processed_files = set()
    st.session_state.image_bytes = {}

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
            st.session_state.image_bytes = {}
    st.session_state.last_uploaded_files = [f.name for f in uploaded_files]


def demo_book_row(file):
    """Return a demo row using fixed values instead of OCR, and store image bytes."""
    img_bytes = file.getvalue()
    st.session_state.image_bytes[file.name] = img_bytes

    # Open once just to validate it is a real image (not needed later)
    _ = Image.open(io.BytesIO(img_bytes))

    return {
        "Image": file.name,
        "Title": DEMO_TITLE,
        "Edition": DEMO_EDITION,
        "Author": DEMO_AUTHOR,
    }


# --- Process Images (demo: fixed values) ---
if uploaded_files:
    for file in uploaded_files:
        if file.name not in st.session_state.processed_files:
            with st.spinner(f"Adding {file.name} to catalogue..."):
                row = demo_book_row(file)
                st.session_state.book_data.append(row)
                st.session_state.processed_files.add(file.name)

    st.success("All images processed (demo values filled in)!")

# --- Editable Table ---
if st.session_state.book_data:
    st.subheader("Editable Book Catalogue")

    df_books = pd.DataFrame(st.session_state.book_data).drop_duplicates()
    edited_df = st.data_editor(df_books, num_rows="dynamic", use_container_width=True)
    st.session_state.book_data = edited_df.to_dict("records")

    # --- Excel Export (with embedded images, no filename text in cells) ---
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Make a copy with the Image column blanked, so only the picture shows
        df_to_export = edited_df.copy()
        if "Image" in df_to_export.columns:
            df_to_export["Image"] = ""

        df_to_export.to_excel(writer, index=False, sheet_name="Catalogue")
        wb = writer.book
        ws = wb["Catalogue"]

        # Add images into column A (Image column)
        # Header row is 1, data starts at row 2
        for row_idx, record in enumerate(st.session_state.book_data, start=2):
            fname = record.get("Image")
            if not fname:
                continue
            img_bytes = st.session_state.image_bytes.get(fname)
            if not img_bytes:
                continue

            # Load, thumbnail, then save to an in-memory PNG buffer
            pil_img = Image.open(io.BytesIO(img_bytes))
            pil_img.thumbnail((120, 120))
            img_buf = io.BytesIO()
            pil_img.save(img_buf, format="PNG")
            img_buf.seek(0)

            xl_img = XLImage(img_buf)
            xl_img.anchor = f"A{row_idx}"  # place image in Image column for this row
            ws.add_image(xl_img)

    output.seek(0)

    file_name = f"{office}_automated_catalogue.xlsx"
    st.download_button(
        "Download Catalogue",
        output,
        file_name,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
