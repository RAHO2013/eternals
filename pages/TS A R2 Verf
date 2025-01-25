import streamlit as st
import pandas as pd
import pdfplumber
import matplotlib.pyplot as plt

# Path to the master file
MASTER_FILE = "tsar2choice.xlsx"  # Ensure the file is in the same directory as this script.

def tsa_comparison():
    st.title("Order Comparison Dashboard")

    # Verify if the master file exists in the folder
    try:
        master_sheet = pd.read_excel(MASTER_FILE, sheet_name=0, dtype=str)

        # Convert specific columns in master_sheet to numeric
        numeric_columns = [
            "sno", "MyRank Order", "Fee", "overall_OPEN", "overall_BCA", "overall_BCB",
            "overall_BCC", "overall_BCD", "overall_BCE", "overall_MSM", "overall_SC",
            "overall_ST", "GEN_OPEN", "FEM_OPEN", "GEN_BCA", "FEM_BCA", "GEN_BCB",
            "FEM_BCB", "GEN_BCC", "FEM_BCC", "GEN_BCD", "FEM_BCD", "GEN_BCE", "FEM_BCE",
            "GEN_MSM", "FEM_MSM", "GEN_SC", "FEM_SC", "GEN_ST", "FEM_ST"
        ]
        for col in numeric_columns:
            if col in master_sheet.columns:
                master_sheet[col] = pd.to_numeric(master_sheet[col], errors='coerce')
    except Exception as e:
        st.error(f"Error loading the master file '{MASTER_FILE}': {e}")
        return

    # File upload section for the PDF file
    uploaded_pdf = st.file_uploader("Upload PDF File for Comparison", type=["pdf"])

    if uploaded_pdf:
        try:
            # Extract data from the PDF
            pdf_data = extract_pdf_data(uploaded_pdf)

            if pdf_data is None or pdf_data.empty:
                st.error("No valid data found in the uploaded PDF file!")
                return

            # Rename columns in the PDF for consistency
            pdf_data.rename(columns={
                "OPTNO": "Order",
                "COLL": "COLL",
                "COLLEGE NAME": "College Name",
                "PLACE": "Place",
                "DIST": "District",
                "CRS": "CRS_pdf",
                "FEE": "Fee Type"
            }, inplace=True)

            # Create MAIN CODE for matching (using COLL and CRS only)
            pdf_data['MAIN CODE'] = pdf_data['COLL'].str.strip() + "_" + pdf_data['CRS_pdf'].str.strip()
            master_sheet['MAIN CODE'] = master_sheet['COLL'].str.strip() + "_" + master_sheet['CRS'].str.strip()

            # Merge data based on MAIN CODE
            merged_data = pd.merge(pdf_data, master_sheet, on='MAIN CODE', how='left', suffixes=('_pdf', '_master'))

            # Tabs for displaying data
            tab1, tab2, tab3, tab4 = st.tabs(["Merged Data", "Student Order Ranges", "Unique Tables by Student Order", "Validation"])

            with tab1:
                display_merged_data(merged_data)

            with tab2:
                display_student_order_ranges(merged_data)

            with tab3:
                display_unique_tables_by_student_order(merged_data)

            with tab4:
                display_validation_tab(merged_data, master_sheet, pdf_data)

        except Exception as e:
            st.error(f"An error occurred while processing the uploaded PDF file: {e}")
    else:
        st.info("Please upload a PDF file for comparison.")

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
        columns = ["OPTNO", "COLL", "COLLEGE NAME", "PLACE", "DIST", "CRS", "FEE"]
        return pd.DataFrame(data_rows, columns=columns)
    else:
        return None

def generate_color_map(unique_values, colormap, alpha=0.3):
    """Generate a color map for unique values using the specified colormap."""
    colors = colormap.colors  # Get colors from the colormap
    color_map = {value: f"background-color: rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, {alpha})"
                 for value, (r, g, b) in zip(unique_values, colors)}
    return color_map

def apply_column_colors(val, color_map):
    """Apply color to a value based on a color map."""
    return color_map.get(val, "")

def display_merged_data(merged_data):
    st.write("### Merged Data")
    merged_data.index = range(1, len(merged_data) + 1)  # Set index starting from 1

    # Generate color maps for each column
    crs_color_map = generate_color_map(merged_data["CRS_pdf"].dropna().unique(), plt.cm.tab20) if "CRS_pdf" in merged_data.columns else {}
    Course_Type_color_map = generate_color_map(merged_data["Course Type"].dropna().unique(), plt.cm.Pastel1) if "Course Type" in merged_data.columns else {}

    # Allow the user to select additional columns to display
    available_columns = merged_data.columns.tolist()
    selected_columns = st.multiselect(
        "Select columns to display:",
        options=available_columns,
        default=available_columns  # Default: display all columns
    )

    if selected_columns:
        filtered_data = merged_data[selected_columns]
        styled_data = filtered_data.style

        # Apply color maps
        if "CRS_pdf" in filtered_data.columns:
            styled_data = styled_data.applymap(lambda val: apply_column_colors(val, crs_color_map), subset=["CRS_pdf"])
        if "Course Type" in filtered_data.columns:
            styled_data = styled_data.applymap(lambda val: apply_column_colors(val, Course_Type_color_map), subset=["Course Type"])

        st.dataframe(styled_data)
    else:
        st.warning("No columns selected!")

def display_student_order_ranges(merged_data):
    st.write("### Student Order Ranges")

    # Ensure required columns exist
    required_columns = ['Order', 'Course Name', 'Course Type', 'Type']
    if not all(col in merged_data.columns for col in required_columns):
        st.error("Required columns for generating the Student Order Ranges are missing!")
        st.write("Detected columns in merged data:", merged_data.columns.tolist())
        return

    # Group by Course Name, Course Type, and Type
    order_ranges_table = merged_data.groupby(['Course Name', 'Course Type', 'Type']).agg(
        Options_Filled=('MAIN CODE', 'count'),
        Student_Order_Ranges=('Order', lambda x: split_ranges(sorted(x.dropna().astype(int).tolist())))
    ).reset_index()

    order_ranges_table['Student_Order_From'] = order_ranges_table['Student_Order_Ranges'].str.extract(r'^([\d]+)', expand=False).astype(float).astype('Int64')
    order_ranges_table['Student_Order_To'] = order_ranges_table['Student_Order_Ranges'].str.extract(r'([\d]+)$', expand=False).astype(float).astype('Int64')
    order_ranges_table['Student_Order_To'].fillna(order_ranges_table['Student_Order_From'], inplace=True)

    # Sort by Student Order From, then Course Name
    order_ranges_table = order_ranges_table.sort_values(by=['Student_Order_From', 'Course Name']).reset_index(drop=True)
    order_ranges_table.index = range(1, len(order_ranges_table) + 1)  # Reset index to start from 1

    # Generate color maps for Course Name and Type columns
    unique_course_names = order_ranges_table["Course Name"].dropna().unique()
    course_name_color_map = generate_color_map(unique_course_names, plt.cm.tab20)

    unique_type_values = order_ranges_table["Type"].dropna().unique()
    type_color_map = generate_color_map(unique_type_values, plt.cm.Pastel1)

    # Style the dataframe
    styled_table = order_ranges_table.style
    styled_table = styled_table.applymap(lambda val: apply_column_colors(val, course_name_color_map), subset=["Course Name"])
    styled_table = styled_table.applymap(lambda val: apply_column_colors(val, type_color_map), subset=["Type"])

    # Display the styled table
    st.dataframe(styled_table)

def display_unique_tables_by_student_order(merged_data):
    st.write("### Unique Tables by Student Order")

    # Dynamically detect the correct column names
    crs_col = next((col for col in merged_data.columns if "CRS" in col), None)
    coll_col = next((col for col in merged_data.columns if "COLL" in col), None)
    fee_type_col = next((col for col in merged_data.columns if "Fee Type" in col), None)
    course_type_col = next((col for col in merged_data.columns if "Course Type" in col), None)
    order_col = next((col for col in merged_data.columns if "Order" in col), None)

    # Check if all required columns exist
    if not all([crs_col, coll_col, fee_type_col, course_type_col, order_col]):
        st.error("Required columns for unique tables are missing in the merged data!")
        st.write("Detected columns in merged data:", merged_data.columns.tolist())
        return

    # Display Course Student Order
    st.write("#### Course Student Order")
    display_grouped_table(merged_data, [crs_col], order_col)

    # Display Fee Type by Student Order
    st.write("#### Fee Type by Student Order")
    display_grouped_table(merged_data, [fee_type_col], order_col)

    # Display Course Type by Student Order
    st.write("#### Course Type by Student Order")
    display_grouped_table(merged_data, [course_type_col], order_col)

    # Display Colleges Student Order
    st.write("#### Colleges Student Order")
    display_grouped_table(merged_data, [coll_col], order_col)

def display_validation_tab(merged_data, master_sheet, pdf_data):
    st.write("### Validation Checks")

    # Check for missing data
    st.write("#### Missing Data in Merged Data")
    missing_data = merged_data.isnull().sum()
    st.write(missing_data)

    # Check for duplicate entries
    st.write("#### Duplicate Entries")
    duplicates = merged_data[merged_data.duplicated(subset='MAIN CODE', keep=False)]
    if not duplicates.empty:
        st.write("Duplicate entries found:")
        st.dataframe(duplicates)
    else:
        st.write("No duplicate entries found.")

    # Check for rows missing in the master file
    st.write("#### Missing Data in Master File")
    missing_in_master = pdf_data[~pdf_data['MAIN CODE'].isin(master_sheet['MAIN CODE'])].reset_index(drop=True)
    if not missing_in_master.empty:
        st.write("Rows in uploaded file missing in the master file:")
        st.dataframe(missing_in_master)
    else:
        st.success("No rows are missing in the master file!")

    # Check for rows missing in the uploaded file
    st.write("#### Missing Data in Uploaded File")
    missing_in_uploaded = master_sheet[~master_sheet['MAIN CODE'].isin(pdf_data['MAIN CODE'])].reset_index(drop=True)
    if not missing_in_uploaded.empty:
        st.write("Rows in master file missing in the uploaded file:")
        st.dataframe(missing_in_uploaded)
    else:
        st.success("No rows are missing in the uploaded file!")

def display_grouped_table(merged_data, group_by_columns, order_column):
    grouped_table = merged_data.groupby(group_by_columns).agg(
        Options_Filled=('MAIN CODE', 'count'),
        First_Student_Order=(order_column, lambda x: sorted(pd.to_numeric(x, errors='coerce').dropna())[0] if not x.isnull().all() else None)
    ).reset_index()

    grouped_table.sort_values(by="First_Student_Order", inplace=True)  # Sort by First Student Order
    grouped_table.index = range(1, len(grouped_table) + 1)  # Reset index to start from 1

    if "Fee Type" in grouped_table.columns:
        unique_fee_type = grouped_table["Fee Type"].dropna().unique()
        fee_type_color_map = generate_color_map(unique_fee_type, plt.cm.Pastel1)
        styled_table = grouped_table.style.applymap(lambda val: apply_column_colors(val, fee_type_color_map), subset=["Fee Type"])
        st.dataframe(styled_table)
    else:
        st.dataframe(grouped_table)

# Helper function to calculate ranges
def split_ranges(lst):
    if not lst:
        return ""
    ranges = []
    start = lst[0]
    for i in range(1, len(lst)):
        if lst[i] != lst[i - 1] + 1:
            end = lst[i - 1]
            ranges.append(f"{start}-{end}" if start != end else f"{start}")
            start = lst[i]
    ranges.append(f"{start}-{lst[-1]}" if start != lst[-1] else f"{start}")
    return ", ".join(ranges)

# Run the app
tsa_comparison()
