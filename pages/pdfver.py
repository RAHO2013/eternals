import streamlit as st
import pandas as pd
import pdfplumber

# Function to extract and consolidate table data from the PDF
def extract_and_consolidate_tables(file):
    consolidated_data = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if table:
                    for row in table:
                        consolidated_data.append(row)
    return consolidated_data

# Streamlit app
st.title("PDF Table Extractor and Unique Value Counter")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    st.write("### Extracting table data...")
    table_data = extract_and_consolidate_tables(uploaded_file)

    if table_data:
        # Ensure consistent row length with header
        header = table_data[0]  # Assuming the first row is the header
        consistent_data = [row for row in table_data[1:] if len(row) == len(header)]

        if consistent_data:
            # Convert consolidated table data into a DataFrame
            df = pd.DataFrame(consistent_data, columns=header)
            st.write("### Consolidated Table:")
            st.dataframe(df)

            # Column selection for unique value count
            column = st.selectbox("Select a column to count unique values:", df.columns)

            if column:
                unique_values_count = df[column].value_counts()
                st.write(f"### Unique Values in Column: {column}")
                st.write(unique_values_count)
        else:
            st.write("No consistent table data found in the PDF.")
    else:
        st.write("No table data found in the PDF.")
