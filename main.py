import streamlit as st
from PIL import Image
import pytesseract

# Optionally, specify the Tesseract executable path if needed:
# pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"  # adjust as needed

st.title("Book OCR Extraction with Manual Field Selection")
st.write("Upload an image of a book. The app will extract text via OCR and then let you choose which lines correspond to the Title, Edition, and Author.")

# Image uploader
uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Open and display the image using use_container_width instead of use_column_width
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
    # Extract text from the image using OCR
    extracted_text = pytesseract.image_to_string(image)
    st.subheader("OCR Extracted Text")
    st.text(extracted_text)
    
    # Split the extracted text into non-empty lines
    lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
    
    if not lines:
        st.warning("No text was extracted from the image. Please try another image or check the image quality.")
    else:
        st.subheader("Select the Appropriate Fields")
        # Let the user choose the title from the list of lines
        title = st.selectbox("Select the Title", lines, index=0)
        # For the edition, add an extra "N/A" option at the beginning of the options list.
        edition_options = ["N/A"] + lines
        edition = st.selectbox("Select the Edition", edition_options, index=0)
        # Let the user choose the author from the list of lines; default to the last line
        author = st.selectbox("Select the Author", lines, index=len(lines)-1)
        
        st.subheader("Extracted Book Information")
        st.write(f"**Title:** {title}")
        st.write(f"**Edition:** {edition}")
        st.write(f"**Author:** {author}")
