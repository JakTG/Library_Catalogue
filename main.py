import streamlit as st
from PIL import Image, ImageEnhance
import pytesseract
import pandas as pd

# Initialize session state to hold book data if it doesn't exist yet
if 'book_data' not in st.session_state:
    st.session_state.book_data = []
st.image("https://www.workspace-interiors.co.uk/application/files/thumbnails/xs/3416/1530/8285/tony_gee_large_logo_no_background.png", width=250)
st.title("Book OCR Extraction with Editable Table")
st.write(
    """
Upload an image of a book. The app will preprocess the image, extract text via OCR, allow you to correct the text and select the Title, Edition, and Author. 
Then, click **Add Book Data** to append the information to a table. You can edit the table and add additional entries by uploading another image.
    """
)

# Image uploader
uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Open the image
    image = Image.open(uploaded_file)
    
    # Preprocess: convert to grayscale and enhance contrast
    gray_image = image.convert("L")
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(2)
    
    # Display the processed image (smaller size)
    st.image(enhanced_image, caption="Processed Image", width=200)
    
    # Perform OCR on the enhanced image
    extracted_text = pytesseract.image_to_string(enhanced_image)
    
    st.subheader("OCR Extracted Text")
    st.text(extracted_text)
    
    # Allow user to edit the extracted text if necessary
    corrected_text = st.text_area("Edit the extracted text if needed", value=extracted_text, height=150)
    
    # Split the (possibly corrected) text into non-empty lines
    lines = [line.strip() for line in corrected_text.splitlines() if line.strip()]
    
    if lines:
        st.subheader("Select the Appropriate Fields")
        title = st.selectbox("Select the Title", lines, index=0)
        edition_options = ["N/A"] + lines
        edition = st.selectbox("Select the Edition", edition_options, index=0)
        author = st.selectbox("Select the Author", lines, index=len(lines)-1)
        
        if st.button("Add Book Data"):
            new_entry = {"Title": title, "Edition": edition, "Author": author}
            st.session_state.book_data.append(new_entry)
            st.success("Book data added to the table!")

# Display the editable table if there is any data
if st.session_state.book_data:
    st.subheader("Catalogued Books")
    # Convert the list of dictionaries to a DataFrame
    df_books = pd.DataFrame(st.session_state.book_data)
    
    # Use the data editor (allows editing) and allow dynamic row edits
    edited_df = st.data_editor(df_books, num_rows="dynamic", key="data_editor")
    
    # Update session state with any changes made in the data editor
    st.session_state.book_data = edited_df.to_dict("records")
