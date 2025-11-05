import streamlit as st
from utils import initialize_session_state, mermaid, add_logo
import extra_streamlit_components as stx
from instructions import INSTRUCTIONS

st.set_page_config(page_title="Socio4Health Data Analysis", page_icon="assets/s4h.ico", layout="wide")
add_logo()

# Initialize session state
initialize_session_state()

with st.expander("ℹ️ Instructions", expanded=False):
    st.markdown(INSTRUCTIONS["home_page"])

# Sidebar
st.sidebar.markdown('Developed by Harmonize team')
st.sidebar.markdown('<a href="mailto:d.irrenotorres@uniandes.edu.co">:email: Contact Us</a>', unsafe_allow_html=True)

# Main content
st.title("Socio4Health Data Analysis 🏘️👥🏥")

st.markdown("""
Welcome to the Socio4Health Data Analysis Pipeline! This powerful tool empowers you to explore, analyze, and gain insights from sociodemographic datasets.
""")

# Workflow diagram
st.header("🔀 Workflow Diagram")

# Use Mermaid diagram for Streamlit 1.10.0 and newer
workflow = """
graph LR
    A[Dictionary Standardization] --> B[Extract Data]
    B --> C[Harmonize Data]
    C --> D[Filter Data]
    C --> E[Vertical & Horizontal Data merge] 
"""
mermaid(workflow)

# Getting Started Guide
st.header("🚀 Getting Started")
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Dictionary Standardization")
    st.markdown("""
    - Navigate to the 'Dictionary Standardization' page
    - Drag and drop your dictionary file or browse files (CSV or Excel)
    - Click 'Standardize Dictionary' to process the file
    - If working with fixed-width files, enable the FWF option and provide column names/specs
    - Download the standardized dictionary for future use as CSV 
    """)

    st.subheader("2. Extract Data")
    st.markdown("""
    - Choice your data source (URL, local file, example database)
    - Enter necessary parameters (e.g., URL, keywords, file extensions, separator, etc.)
    - Process the data 
    """)

with col2:
    st.subheader("3. Harmonize Data")
    st.markdown("""
    - Visit the 'Harmonizer' page

    """)

# Tips and Notes
st.header("💡 Tips")
tips = st.container()

with tips:
    tip1, tip2, tip3 = st.columns(3)

    with tip1:
        st.info("**Data Types**: The app supports various data formats including CSV, Excel, and databases.")

    with tip2:
        st.success("**Save Your Work**: You can download processed data at various stages of the analysis.")

# Dataset Information
st.header("📚 Available Datasets")
st.markdown("""
The following datasets are currently available for analysis:
- COVID-19 Colombian Data
- Colombian People Census Data
- Custom datasets (upload your own)

Explore these datasets to uncover valuable insights about public health and demographics.
""")

# Footer
st.markdown("---")
st.markdown("© 2025 Socio4Health. All rights reserved.")