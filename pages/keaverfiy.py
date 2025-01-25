import streamlit as st
import pandas as pd
import camelot

def extract_pdf_data(uploaded_pdf):
    """Extract tabular data from the uploaded PDF file using Camelot."""
    try:
        # Save the uploaded file to a temporary location
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_pdf.read())
        
        # Extract tables using Camelot
        tables = camelot.read_pdf("temp.pdf", pages="all", flavor="stream")
        
        if len(tables) == 0:
            return None
        
        # Concatenate all extracted tables into a single DataFrame
        data_frames = [table.df for table in tables]
        combined_df = pd.concat(data_frames, ignore_index=True)
        
        # Rename columns based on your PDF's structure
        if len(combined_df.columns) >= 6:
            combined_df.columns = ["Optn. No", "College Code", "Course Code", 
                                   "Course Name", "Course Fee per Annum (Rs)", 
                                   "College Name"]
            return combined_df
        else:
            st.warning("Extracted table has fewer columns than expected.")
            return combined_df
    except Exception as e:
        st.error(f"An error occurred while extracting tables: {e}")
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
    st.title("PDF Table Extraction Tool with Camelot")
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
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
