import streamlit as st
from PIL import Image, ImageEnhance
import pytesseract

# Uncomment and adjust the following line if Tesseract isn't in your PATH
# pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

st.title("Book OCR Extraction Debugging")
st.write("Upload an image of a book. The app will try to extract text via OCR.")

uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
    # Preprocess the image: Convert to grayscale and enhance contrast
    gray_image = image.convert('L')
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(2)
    
    # Display the processed image for debugging
    st.image(enhanced_image, caption="Processed Image (Grayscale & Enhanced)", use_container_width=True)
    
    # Extract text using pytesseract
    extracted_text = pytesseract.image_to_string(enhanced_image)
    
    st.subheader("OCR Extracted Text")
    st.text(extracted_text)
    
    # If text is extracted, split into lines for manual selection
    lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
    
    if not lines:
        st.warning("No text was extracted from the image. Check image quality or Tesseract installation.")
    else:
        st.subheader("Select the Appropriate Fields")
        title = st.selectbox("Select the Title", lines, index=0)
        edition_options = ["N/A"] + lines
        edition = st.selectbox("Select the Edition", edition_options, index=0)
        author = st.selectbox("Select the Author", lines, index=len(lines)-1)
        
        st.subheader("Extracted Book Information")
        st.write(f"**Title:** {title}")
        st.write(f"**Edition:** {edition}")
        st.write(f"**Author:** {author}")
