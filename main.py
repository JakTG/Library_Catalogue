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
    st.write("""
        **Enter your book data in CSV format in the text box below.**
        
        Each book should provide three pieces of information in this order:
        - **Name**
        - **Edition** (enter "N/A" if not applicable)
     
