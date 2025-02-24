import streamlit as st
from PIL import Image, ImageEnhance
import pytesseract

st.title("Book OCR Extraction with Manual Correction")
st.write("Upload an image of a book. The app will process the image (grayscale & contrast enhanced), extract text via OCR, and let you correct the text if needed.")

# Image uploader
uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Open the uploaded image
    image = Image.open(uploaded_file)
    
    # Preprocess the image: convert to grayscale and enhance contrast
    gray_image = image.convert("L")
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(2)
    
    # Display the processed image only
    st.image(enhanced_image, caption="Processed Image (Grayscale & Enhanced)", use_container_width=True)
    
    # Perform OCR on the enhanced image
    extracted_text = pytesseract.image_to_string(enhanced_image)
    
    st.subheader("OCR Extracted Text")
    st.text(extracted_text)
    
    # Allow user to edit the OCR text in case it's incomplete or needs correction
    corrected_text = st.text_area("Edit the extracted text if needed", value=extracted_text, height=150)
    
    # Split the (possibly corrected) text into non-empty lines
    lines = [line.strip() for line in corrected_text.splitlines() if line.strip()]
    
    if not lines:
        st.warning("No text was provided. Please check the image quality or enter text manually.")
    else:
        st.subheader("Select the Appropriate Fields")
        # Let the user choose the Title from the list of lines
        title = st.selectbox("Select the Title", lines, index=0)
        # For Edition, add a "N/A" option plus all extracted lines
        edition_options = ["N/A"] + lines
        edition = st.selectbox("Select the Edition", edition_options, index=0)
        # Let the user choose the Author; default to the last line
        author = st.selectbox("Select the Author", lines, index=len(lines)-1)
        
        st.subheader("Extracted Book Information")
        st.write(f"**Title:** {title}")
        st.write(f"**Edition:** {edition}")
        st.write(f"**Author:** {author}")
