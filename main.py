import streamlit as st
import io
import csv
import pandas as pd

# Display picture
st.image("https://www.workspace-interiors.co.uk/application/files/thumbnails/xs/3416/1530/8285/tony_gee_large_logo_no_background.png", width=250)

# Title and description
st.title("Tony Gee, Library Catalogue Automation")
st.write("Enter information on your books to catalogue manually.")

# Office selection drop-down
office = st.selectbox("Select Office", ["Manchester", "Esher", "Birmingham", "Stonehouse"])

# Expander for usage instructions
with st.expander("How to use"):
    st.write(
        """
**Enter your book data in CSV format in the text box below.**

Each book should provide three pieces of information in this order:
- **Name**
- **Edition** (enter "N/A" if not applicable)
- **Author**

**Note:** If the Author field contains commas (for example, for multiple authors), enclose the entire field in double quotes.
        """
    )

# Input text area for book data
book_data = st.text_area(
    "Enter Book Data",
    '''WW1,1st edition,"Simons, Menzies and Matthews"
Advanced National Certificate,N/A,Pedoe
Modern Architecture,N/A,"Smith, Johnson, and Lee"'''
)

# Process input and generate output
if st.button("Submit Book Data"):
    books = []
    f = io.StringIO(book_data)
    reader = csv.reader(f, skipinitialspace=True)
    for row in reader:
        if len(row) != 3:
            st.error("Each line must contain exactly three fields: Name, Edition, and Author.")
            books = []  # Reset if error is encountered
            break
        name, edition, author = row
        books.append({"Name": name, "Edition": edition, "Author": author})
    
    if books:
        df_books = pd.DataFrame(books)
        st.write("Catalogued Books:")
        st.dataframe(df_books)
        
        # Create an Excel file from the DataFrame using an in-memory bytes buffer
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_books.to_excel(writer, index=False, sheet_name='Catalogued Books')
            writer.save()
        excel_data = output.getvalue()
        file_name = f"{office}_catalogued_library.xlsx"
        
        # Download button for Excel file
        st.download_button("Download Catalogued Books Excel", excel_data, file_name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
