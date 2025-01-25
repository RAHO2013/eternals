import streamlit as st
import pandas as pd
import pdfplumber

def extract_pdf_data(uploaded_pdf):
    """Extract tabular data from the uploaded PDF file using pdfplumber."""
    with pdfplumber.open(uploaded_pdf) as pdf:
        data_rows = []
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                # Skip the header row and append the rest
                data_rows.extend(table[1:])

    if data_rows:
        # Define columns based on the structure of the PDF
        columns = ["Optn. No", "College Code", "Course Code", "Course Name", 
                   "Course Fee per Annum (Rs)", "College Name"]
        return pd.DataFrame(data_rows, columns=columns)
    else:
        return None

def display_data_table(data):
    """Display the extracted data in a Streamlit dataframe."""
    st.write("### Extracted Data")
    if data is not None and not data.empty:
        st.dataframe(data)
    else:
        st.error("No valid data found in the uploaded PDF file!")

def generate_summary(data):
    """Generate a summary of the data."""
    if data is not None and not data.empty:
        st.write("### Summary")
        # Summary by course name
        course_summary = data["Course Name"].value_counts().reset_index()
        course_summary.columns = ["Course Name", "Number of Options"]
        st.write("#### Course-wise Summary")
        st.table(course_summary)

        # Summary by college
        college_summary = data["College Name"].value_counts().reset_index()
        college_summary.columns = ["College Name", "Number of Options"]
        st.write("#### College-wise Summary")
        st.table(college_summary)

def main():
    st.title("PDF Table Extraction Tool")
    st.write("Upload a PDF file to extract tabular data.")
    
    uploaded_pdf = st.file_uploader("Upload PDF File", type=["pdf"])
    
    if uploaded_pdf:
        try:
            # Extract data from the PDF
            extracted_data = extract_pdf_data(uploaded_pdf)
            
            # Display the extracted data
            display_data_table(extracted_data)
            
            # Generate and display summary statistics
            generate_summary(extracted_data)
            
        except Exception as e:
            st.error(f"An error occurred while processing the PDF: {e}")

if __name__ == "__main__":
    main()
