import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import pandas as pd
import io

# --- Session State Init ---
if "ocr_data" not in st.session_state:
    st.session_state.ocr_data = []

st.title("OCR Line-by-Line Accuracy Tester")
st.write("Upload an image. The app extracts ALL text and splits it into clean lines.")

uploaded_files = st.file_uploader(
    "Upload test images",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# -------------------------
# BETTER OCR PREPROCESSING (no cv2 needed)
# -------------------------
def preprocess_image(img):
    # Convert to grayscale
    img = img.convert("L")

    # Increase contrast
    img = ImageEnhance.Contrast(img).enhance(2.5)

    # Sharpen image
    img = ImageEnhance.Sharpness(img).enhance(2.0)

    # Slight noise reduction
    img = img.filter(ImageFilter.MedianFilter(size=3))

    # Upscale for better OCR
    w, h = img.size
    img = img.resize((w * 2, h * 2))

    return img

# -------------------------
# RUN OCR
# -------------------------
if uploaded_files:
    st.session_state.ocr_data = []  # Reset

    for file in uploaded_files:
        img = Image.open(file)
        processed = preprocess_image(img)

        # OCR configuration
        config = "--oem 3 --psm 6"

        text = pytesseract.image_to_string(processed, config=config)

        # Split into clean lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Create row dictionary
        row = {"Image": file.name}

        # Add each line into its own column
        for i, line in enumerate(lines):
            row[f"Line {i+1}"] = line

        st.session_state.ocr_data.append(row)

    st.success("OCR Completed!")

# -------------------------
# DISPLAY RESULTS
# -------------------------
if st.session_state.ocr_data:
    df = pd.DataFrame(st.session_state.ocr_data)
    st.data_editor(df, use_container_width=True)

    # Excel export
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="OCR Lines")
    output.seek(0)

    st.download_button(
        "Download OCR Lines Excel",
        output,
        "ocr_lines.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
