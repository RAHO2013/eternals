import streamlit as st
import pandas as pd
import pdfplumber
import re

def extract_college_course_and_student_details(file):
    # Read the uploaded PDF file
    lines = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                lines.extend(extracted_text.splitlines())

    # Initialize variables
    structured_data = []
    current_college_code = ""
    current_college_name = ""
    current_course_code = ""
    current_course_name = ""

    for line in lines:
        line = line.strip()

        # Skip empty or dashed lines
        if not line or "-----" in line:
            continue

        # Capture college details from COLL ::
        if line.startswith("COLL ::"):
            parts = line.split(" - ")
            current_college_code = parts[0].replace("COLL ::", "").strip()
            current_college_name = parts[1].strip() if len(parts) > 1 else ""

        # Capture course details from CRS ::
        elif line.startswith("CRS ::"):
            parts = line.split(" - ")
            current_course_code = parts[0].replace("CRS ::", "").strip()
            current_course_name = parts[1].strip() if len(parts) > 1 else ""

        # Process student rows based on specific rules
        else:
            try:
                # Start extracting from the rightmost elements
                # Match admission details (starts with NS- or S- and ends with -P1, -P2, -P3, or -P4)
                adm_details_match = re.search(r"(NS-|S-).*(-P1|-P2|-P3|-P4)$", line)
                adm_details = adm_details_match.group(0) if adm_details_match else ""
                remaining_line = line[:line.rfind(adm_details)].strip() if adm_details else line

                # Match PH (PHO or blank)
                ph_match = re.search(r"(PHO)", remaining_line)
                ph = ph_match.group(1) if ph_match else ""
                remaining_line = remaining_line[:remaining_line.rfind(ph)].strip() if ph else remaining_line

                # Match MIN (MSM or blank)
                min_match = re.search(r"(MSM)", remaining_line)
                min_status = min_match.group(1) if min_match else ""
                remaining_line = remaining_line[:remaining_line.rfind(min_status)].strip() if min_status else remaining_line

                # Match sex (F or M), ensuring it is valid and not part of another field
                sex_match = re.search(r"(F|M)(\s|$)", remaining_line)
                sx = sex_match.group(1) if sex_match else ""
                remaining_line = remaining_line[:remaining_line.rfind(sx)].strip() if sx else remaining_line

                # Extract remaining fields from left to right
                # Match rank (1 to 6 digits)
                rank_match = re.match(r"^(\d{1,6})\s", remaining_line)
                if not rank_match:
                    continue
                rank = rank_match.group(1)

                # Match roll number (11 digits starting with 24)
                roll_no_match = re.search(r"(24\d{9})", remaining_line)
                if not roll_no_match:
                    continue
                roll_no = roll_no_match.group(1)

                # Match percentile (a floating-point number after roll number)
                percentile_match = re.search(r"(\d+\.\d+)", remaining_line[roll_no_match.end():])
                if not percentile_match:
                    continue
                percentile = percentile_match.group(1)

                # Match candidate name (all letters between percentile and location)
                candidate_name_start = remaining_line.find(percentile) + len(percentile)
                candidate_name_end = remaining_line.find("OU", candidate_name_start)
                if candidate_name_end == -1:
                    continue
                candidate_name = remaining_line[candidate_name_start:candidate_name_end].strip()

                # Match location (fixed "OU")
                loc = "OU"

                # Match category (specific categories allowed)
                category_match = re.search(r"(BCA|BCB|BCD|BCC|BCE|ST|SC|OC)", remaining_line[candidate_name_end:])
                if not category_match:
                    continue
                cat = category_match.group(1)

                # Append structured row
                structured_data.append([
                    current_college_code, current_college_name,
                    current_course_code, current_course_name,
                    rank, roll_no, percentile, candidate_name,
                    loc, cat, sx, min_status, ph, adm_details
                ])
            except Exception as e:
                print(f"Error processing line: {line}, Error: {e}")
                continue

    # Define DataFrame columns
    columns = [
        "College Code", "College Name", "Course Code", "Course Name",
        "Rank", "Roll Number", "Percentile", "Candidate Name",
        "Location", "Category", "Sex", "MIN", "PH", "Admission Details"
    ]

    # Create DataFrame
    df = pd.DataFrame(structured_data, columns=columns)
    return df

# Streamlit interface
st.title("College, Course, and Student Details Extractor")

uploaded_file = st.file_uploader("Upload your admissions PDF file", type=["pdf"])

if uploaded_file is not None:
    # Extract college, course, and student details
    df = extract_college_course_and_student_details(uploaded_file)

    if not df.empty:
        # Display the DataFrame
        st.write("### Extracted College, Course, and Student Details")
        st.dataframe(df)

        # Allow user to download the Excel file
        excel_file = "structured_admissions_data.xlsx"
        df.to_excel(excel_file, index=False)
        with open(excel_file, "rb") as file:
            st.download_button(
                label="Download Excel File",
                data=file,
                file_name="structured_admissions_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.error("No data extracted. Check the PDF format and content.")
