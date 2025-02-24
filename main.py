import streamlit as st
import os
import shutil
import AutomationReport 
from zipfile import ZipFile

def delete_folder(folder_path):
    try:
        shutil.rmtree(folder_path)  # Remove the folder and all its contents (files and subdirectories)
        print(f'Folder {folder_path} deleted successfully.')
    except Exception as e:
        print(f'Failed to delete {folder_path}. Reason: {e}')

#delete folders
delete_folder("DWG_Reports")
delete_folder("Output_Reports")

# Folder where the uploaded files will be saved
# Create the folder if it doesn't exist
upload_folder = "DWG_Reports"
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)
output_folder = "Output_Reports"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Streamlit title and description
st.image("https://www.workspace-interiors.co.uk/application/files/thumbnails/xs/3416/1530/8285/tony_gee_large_logo_no_background.png",width=250)
st.title("Tony Gee Manchester, Power and energy")
st.write("Drag and drop CSV files below to upload them.")

# File uploader widget (allows multiple files)
uploaded_files = st.file_uploader("Upload Files", type=None, accept_multiple_files=True)

# Variable to track if files were uploaded
files_uploaded = False

# Process and save each uploaded file
if uploaded_files:
    for uploaded_file in uploaded_files:
        # Get the file details
        file_name = uploaded_file.name
        file_path = os.path.join(upload_folder, file_name)

        # Save the uploaded file to the folder
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Show a success message for each uploaded file
        st.success(f"File '{file_name}' uploaded successfully!")

    # Set flag to true if files have been uploaded
    files_uploaded = True

# Display a button to run code if files have been uploaded
if files_uploaded:
    # Show a button
    if st.button("Process Uploaded Files"):
        # Your custom code goes here
        st.write("Processing files...")

        # Example: Just list the files in the uploaded folder
        for fileRead in os.listdir(upload_folder):
            st.write(f"Processing file: {fileRead}")
            AutomationReport.main(fileRead)

        # Add custom logic here to process the uploaded files
        st.success("File processing complete!")

        zip_path = "processed_files.zip"
        with ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(output_folder):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=file)
        
        # 4. Add Download Button for Processed Files
        with open(zip_path, "rb") as f:
            st.download_button(label="Download Processed Files", 
                               data=f, 
                               file_name="processed_files.zip")