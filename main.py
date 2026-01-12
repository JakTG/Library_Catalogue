# Packages used for the code
import streamlit as st
from PIL import Image, UnidentifiedImageError
import pandas as pd
import io
from openpyxl.drawing.image import Image as XLImage  # for embedding images into Excel

# --- DEMO CONSTANTS (change these later if needed) ---
DEMO_TITLE = "The use of Stereographic Projection in Structural Geology"
DEMO_EDITION = "3rd Edition"
DEMO_AUTHOR = "F.C.Phillips"


# ---------- Helpers ----------
def safe_open_pil_image(img_bytes: bytes):
    """
    Safely open uploaded image bytes with PIL.
    Returns a PIL.Image.Image or None if invalid/corrupt/unsupported.
    """
    try:
        # First open + verify to catch truncated/invalid image files early
        bio = io.BytesIO(img_bytes)
        im = Image.open(bio)
        im.verify()  # verifies file integrity, but leaves the image file closed/unusable

        # Re-open after verify to actually use the image
        bio2 = io.BytesIO(img_bytes)
        im2 = Image.open(bio2)

        # Force-load the image data now (helps catch some deferred decode errors)
        im2.load()
        return im2
    except (UnidentifiedImageError, OSError, ValueError):
        return None


def pil_to_excel_image(pil_img: Image.Image, max_size=(120, 120)) -> io.BytesIO:
    """
    Make a thumbnail and return a PNG buffer ready for openpyxl XLImage().
    """
    img = pil_img.copy()
    img.thumbnail(max_size)

    # Ensure it's in a PNG-friendly mode
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


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
    """
    Return a demo row using fixed values instead of OCR, and store image bytes.
    Skips invalid/corrupt image uploads safely (prevents PIL.UnidentifiedImageError).
    """
    img_bytes = file.getvalue()

    # Validate it's a real image before storing/using it
    pil_img = safe_open_pil_image(img_bytes)
    if pil_img is None:
        st.warning(f"Skipped '{file.name}': not a valid/decodable image (may be corrupt or mislabeled).")
        return None

    st.session_state.image_bytes[file.name] = img_bytes

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
                # Mark as processed either way to avoid retry loops on bad files
                st.session_state.processed_files.add(file.name)

                if row is not None:
                    st.session_state.book_data.append(row)

    if st.session_state.book_data:
        st.success("All valid images processed!")
    else:
        st.info("No valid images were processed. Please upload PNG/JPG/JPEG images that open normally.")

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

        # Make the Image column reasonably wide (Excel width units)
        ws.column_dimensions["A"].width = 18  # tweak this if you want wider/narrower

        # Add images into column A (Image column)
        # Header row is 1, data starts at row 2
        for row_idx, record in enumerate(st.session_state.book_data, start=2):
            fname = record.get("Image")
            if not fname:
                continue

            img_bytes = st.session_state.image_bytes.get(fname)
            if not img_bytes:
                continue

            pil_img = safe_open_pil_image(img_bytes)
            if pil_img is None:
                # If the image is somehow invalid at export time, skip it instead of crashing
                continue

            # Create thumbnail buffer for Excel
            img_buf = pil_to_excel_image(pil_img, max_size=(120, 120))
            xl_img = XLImage(img_buf)
            xl_img.anchor = f"A{row_idx}"  # place image in Image column for this row
            ws.add_image(xl_img)

            # Adjust row height to roughly match the thumbnail height
            thumb_h_px = min(pil_img.size[1], 120)  # thumbnail height won't exceed 120
            ws.row_dimensions[row_idx].height = thumb_h_px * 0.75

    output.seek(0)

    file_name = f"{office}_automated_catalogue.xlsx"
    st.download_button(
        "Download Catalogue",
        output,
        file_name,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

