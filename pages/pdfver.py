import streamlit as st
import pandas as pd
import pdfplumber

# Function to extract table data from the PDF
def extract_table_from_pdf(file):
    table_data = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    table_data.append(row)
    return table_data

# Streamlit app
st.title("PDF Table Extractor and Unique Value Counter")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    st.write("### Extracting table data...")
    table_data = extract_table_from_pdf(uploaded_file)

    if table_data:
        # Convert table data into a DataFrame
        df = pd.DataFrame(table_data[1:], columns=table_data[0])  # Assuming the first row is the header
        st.write("### Extracted Table:")
        st.dataframe(df)

        # Column selection for unique value count
        column = st.selectbox("Select a column to count unique values:", df.columns)

        if column:
            unique_values_count = df[column].value_counts()
            st.write(f"### Unique Values in Column: {column}")
            st.write(unique_values_count)
    else:
        st.write("No table data found in the PDF.")
