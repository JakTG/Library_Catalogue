import streamlit as st
from PIL import Image, ImageEnhance
import pytesseract
import pandas as pd
import io

# Initialize session state to hold book data if it doesn't exist yet
if 'book_data' not in st.session_state:
    st.session_state.book_data = []

# Title and description
st.image("https://www.workspace-interiors.co.uk/application/files/thumbnails/xs/3416/1530/8285/tony_gee_large_logo_no_background.png", width=250)
st.title("Book OCR Extraction with Editable Catalogue")
st.write("Automated app to extract information from images using OCR, allowing users to correct fields and compile everything into a ready made excel file.")

# How the app works expander
with st.expander("How the app works"):
    st.write(
        """
1. **Upload an Image:** Upload an image of a book. The app preprocesses the image.
2. **OCR Extraction:** The app extracts text using OCR. You can edit the extracted text if needed.
3. **Select Fields:** Choose the appropriate lines for the Title, Edition (with an extra "N/A" option), and Author.
4. **Add Book Data:** Click **Add Book Data** to append the information to the catalogue table.
5. **Select Office:** Use the drop-down to select your office.
6. **Download Catalogue:** Click **Process & Download Catalogue** to download the table as an Excel file with all your catalogued information.
        """
    )

# Office selection drop-down
office = st.selectbox("Select Your Office", ["Manchester", "Esher", "Birmingham", "Stonehouse"])

# Image uploader, change these file types
uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Open the image
    image = Image.open(uploaded_file)
    
    # Preprocess: convert to grayscale and enhance contrast, change this, it may be stopping the visiblility of the image that is being uploaded
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
    st.subheader("Catalogue of Books")
    df_books = pd.DataFrame(st.session_state.book_data)
    edited_df = st.data_editor(df_books, num_rows="dynamic", key="data_editor")
    st.session_state.book_data = edited_df.to_dict("records")

# Process & Download Catalogue Button
if st.session_state.book_data:
    if st.button("Process & Download Catalogue"):
        # Convert the DataFrame to an Excel file in-memory using openpyxl
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_books.to_excel(writer, index=False, sheet_name='Catalogue')
        excel_data = output.getvalue()
        file_name = f"{office}_automated_catalogue.xlsx"
        st.download_button("Download Catalogue", excel_data, file_name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
