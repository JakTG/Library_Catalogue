import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import pandas as pd
import io
import numpy as np
import cv2

# Init session state
if "ocr_results" not in st.session_state:
    st.session_state.ocr_results = []

st.title("OCR Accuracy Tester")
st.write("Upload ANY image and this tool will extract ALL readable text clearly.")

uploaded_files = st.file_uploader(
    "Upload test images",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# -------------------------
# BETTER OCR PREPROCESSING
# -------------------------
def preprocess(image):
    # Convert to OpenCV
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Adaptive thresholding (WAY better)
    img = cv2.adaptiveThreshold(
        img, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 10
    )

    # Denoise
    img = cv2.fastNlMeansDenoising(img, h=15)

    # Resize (improves OCR massively)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    return img

# -------------------------
# PROCESS EACH IMAGE
# -------------------------
if uploaded_files:
    st.session_state.ocr_results = []  # reset

    for file in uploaded_files:
        image = Image.open(file)
        processed = preprocess(image)

        # OCR config
        config = "--oem 3 --psm 6"

        text = pytesseract.image_to_string(processed, config=config)

        st.session_state.ocr_results.append({
            "Image": file.name,
            "Extracted Text": text.strip()
        })

    st.success("Images processed!")

# -------------------------
# DISPLAY RESULTS
# -------------------------
if st.session_state.ocr_results:
    df = pd.DataFrame(st.session_state.ocr_results)
    st.data_editor(df, use_container_width=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="OCR Results")
    output.seek(0)

    st.download_button(
        "Download OCR Results",
        output,
        "ocr_results.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
