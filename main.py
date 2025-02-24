import streamlit as st
import io
import csv
import pandas as pd

# Display picture
st.image("https://www.workspace-interiors.co.uk/application/files/thumbnails/xs/3416/1530/8285/tony_gee_large_logo_no_background.png", width=250)

# Title and Description
st.title("Tony Gee, Library Catalogue Automation")
st.write("Enter information on your books to catalogue manually.")

# Office selection drop-down
office = st.selectbox("Select Office", ["Manchester", "Esher", "Birmingham", "Stonehouse"])

# Instructions for entering book data
st.write("""
Enter book data in CSV format.  
Each line should contain three fields in this order:  
1. **Name**  
2. **Edition** (enter "N/A" if not applicable)  
3. **Author**  

If a field (such as Author) contains commas (for example, for multiple authors), enclose that field in double quotes.
""")

# Input text area for book data
book_data = st.text_area(
    "Enter Book Data",
    '''WW1,1st edition,"Simons, Menzies and Matthews"
Advanced National Certificate,N/A,Pedoe
Modern Architecture,N/A,"Smith, Johnson, and Lee"'''
)

# Process the input and generate the catalogued table and download button
if st.button("Submit Book Data"):
    books = []
    f = io.StringIO(book_data)
    reader = csv.reader(f, skipinitialspace=True)
    for row in reader:
        if len(row) != 3:
            st.error("Each line must contain exactly three fields: Name, Edition, and Author.")
            books = []  # Reset if an error is encountered
            break
        name, edition, author = row
        books.append({"Name": name, "Edition": edition, "Author": author})
    
    if books:
        df_books = pd.DataFrame(books)
        st.write("Catalogued Books:")
        st.dataframe(df_books)
        # Create a CSV file from the DataFrame for download
        csv_file = df_books.to_csv(index=False).encode("utf-8")
        file_name = f"{office}_catalogued_library.csv"
        st.download_button("Download Catalogued Books CSV", csv_file, file_name, "text/csv")
