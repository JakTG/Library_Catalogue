# Packages- look into adding Open AI API
import streamlit as st
from PIL import Image, ImageEnhance
import pytesseract
import pandas as pd
import io
# import Img_folder

# Integrate OpenAI API- to automate the task of adding the data- it may not be necessary as it is required to do typo errors etc
# Instead of just trying to read the image- try to extract the text out of the image- may remove the difficulty with reading fonts and watermarks
# Binary threshold with OCR make sure to change


# File paths- maybe just use a folder and import the image folder

# Initialize session state to hold book data if it doesn't exist yet
if 'book_data' not in st.session_state:
    st.session_state.book_data = []

# Title and description
st.image("https://www.workspace-interiors.co.uk/application/files/thumbnails/xs/3416/1530/8285/tony_gee_large_logo_no_background.png", width=250)
st.title("Book OCR Extraction with Editable Catalogue")
st.write("Automated app to extract information from images using OCR, allowing users to correct fields and compile everything into a ready made excel file.")

# How the app works expander
with st.expander("How to use the app "):
    st.write(
        """
1. Upload folder of images of books/barcodes ready to be scanned
2. Select the office you are from to extract the books accordingly
3. Pytesseract OCR will be used to read the images that you have inputted
4. An Automated catalogued library will appear with all the information from your images uploaded
5. Download the catalogue library and it will be exported into a xlsx file ready to be used
        """
    )

# Office selection drop-down
office = st.selectbox("Select Your Office", ["Manchester", "Esher", "Birmingham", "Stonehouse"])

# Image uploader, change these file types
uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_file:
    # Open the image
    image = Image.open(uploaded_file)
    
    # Preprocess: convert the image maybe to Binary thresh so then it picks up the image better. At the minute the picture is reading certain things but not everything in 
    # convert image back to colour and change font- take into consideration the quality of the picture it could affect the OCR image
    enhancer = ImageEnhance.Contrast(image)
    enhanced_image = enhancer.enhance(2)
    final_image = image.convert('1')
    
    # Display the processed image (smaller size)
    st.image(enhanced_image, caption="Processed Image", width=200)
    
    # Perform OCR on the enhanced image, check if this configuration can be configed to psm 6 to improve accuracy
    extracted_text = pytesseract.image_to_string(enhanced_image) # config='--psm 6'
    
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



        # integrate Open AI API, once the button is clicked it will automate the process of adding it to the excel
        if st.button("Add Book Data"):
            new_entry = {"Image": image, "Title": title, "Edition": edition, "Author": author}
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



# For loop to allow the loop from all of the images- include this in the function so that it will pass a parameter into the function, going to loop through the 
# For images in Img_folder:
    # Process_image = 
    # Process_image.append()- to the excel spreadsheet, first to the catalogue



#########################################
# For loop requirements-
#1) Loop through all of the folder to cycle through images
#2) Call the OCR function to perform the image reading process




########################################
# Improving quality techniques
# 1) Converting image to gray scale- Done
# 2) changing the threshold of the image and using Binary and OTSU packages
# 3) Configuring the image to string- '--psm 6'
# 4) Binary thresh- could be used to make the image nothing but the text- can help with removing watermarks 
# 5) OpenAI API to allow the automation of adding the items to the catalogue





