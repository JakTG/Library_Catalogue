import streamlit as st
from PIL import Image
import pytesseract

# Optionally, specify the Tesseract executable path if not in your PATH:
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
st.image("https://www.workspace-interiors.co.uk/application/files/thumbnails/xs/3416/1530/8285/tony_gee_large_logo_no_background.png", width=250)

st.title("Tony Gee, library catalogue automation")
st.write("Upload an image of a book. The app will extract text via OCR and then let you choose which lines correspond to the Title, Edition, and Author.")

# Image uploader
uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Open and display the image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    # Extract text from the image using OCR
    extracted_text = pytesseract.image_to_string(image)
    st.subheader("OCR Extracted Text")
    st.text(extracted_text)
    
    # Split the extracted text into non-empty lines
    lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
    
    if lines:
        st.subheader("Select the Appropriate Fields")
        # For the Title and Author, use the OCR lines as options.
        title = st.selectbox("Select the Title", lines, index=0)
        author = st.selectbox("Select the Author", lines, index=len(lines)-1)
        
        # For the Edition, add an extra "N/A" option to the list.
        edition_options = ["N/A"] + lines
        edition = st.selectbox("Select the Edition", edition_options, index=0)
        
        st.subheader("Extracted Book Information")
        st.write(f"**Title:** {title}")
        st.write(f"**Edition:** {edition}")
        st.write(f"**Author:** {author}")
