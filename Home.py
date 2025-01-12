import streamlit as st

st.title("Welcome to ETERNALS")

# Insert an image from the 'data' folder with the updated parameter
st.image("pages/maxresdefault.jpg", caption="ETERNALS", use_container_width=True)
st.markdown("""
    ## Home Page
    Welcome to **ETERNALS**! 🎉


    ### Features:
    - **📊 Master Data**: View and manage your master dataset.
    - **🔍 Comparison Tools**: Compare data using advanced features.
    - **💸 Fee Checking**: Analyze and validate fee structures.

    ### How to Navigate:
    Use the **Sidebar** on the left to:
    - Select different sections.
    - Group related functionalities under expandable menus for clarity.

    ---
    **Start Exploring Now!**
    """)
st.balloons()
