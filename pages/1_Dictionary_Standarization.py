import streamlit as st
import pandas as pd
from socio4health.utils import extractor_utils, harmonizer_utils

from utils import initialize_session_state, show_session_state, add_logo


def dictionary_standardization(df):
    """
    Standardize a dictionary dataframe using harmonizer utilities.

    Parameters:
    df (pd.DataFrame): Raw dictionary dataframe

    Returns:
    pd.DataFrame: Standardized dictionary
    """
    if df is not None:
        return harmonizer_utils.s4h_standardize_dict(df)
    return None


st.set_page_config(page_title="Dictionary Standardization", page_icon="assets/s4h.ico", layout="wide")
add_logo()

initialize_session_state()

st.title("Dictionary Standardization 📖")

# Beginner-friendly guide: simple, short, step-by-step
with st.expander("Instructions", expanded=True):
    st.markdown(
        """
        **What is a dictionary?**

        A dictionary is a table that tells the program what each column in your data means.

        **What does 'standardize' mean?**

        It means we clean and rename the columns so they follow the project's rules. This makes different files behave the same way.

        **Easy steps (like a recipe):**

        1. Choose a file (CSV or Excel) using the uploader below.
        2. Click the "Standardize Dictionary" button. The app will try to tidy column names and types.
        3. If your data is a fixed-width file, turn on "Is this a fixed width file?" to see column names and positions.
        4. Download the standardized dictionary using the button in "Download Options".

        **If something goes wrong:**

        - Make sure the file is CSV or XLSX and that the first row contains column names.
        - If the app shows an error while parsing fixed-width, the dictionary might miss width information or have unexpected values.
        """
    )

# File uploader
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

raw_dic = None
if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        raw_dic = pd.read_csv(uploaded_file)
    else:
        raw_dic = pd.read_excel(uploaded_file)

if raw_dic is not None:
    if st.button("Standardize Dictionary"):
        with st.spinner("Standardizing dictionary..."):
            standardized_dic = dictionary_standardization(raw_dic)
            if standardized_dic is not None:
                st.session_state.standardized_dict = standardized_dic
                st.success("Dictionary standardized successfully!")

                st.write("Standardized Dictionary Preview:")
                st.dataframe(standardized_dic.head())
            else:
                st.error("Failed to standardize dictionary.")


if st.session_state.standardized_dict is not None:
    st.subheader("Fixed Width File Options")
    is_fwf = st.toggle("Is this a fixed width file?")

    if is_fwf:
        try:
            st.session_state.is_fwf = is_fwf
            colnames, colspecs = extractor_utils.s4h_parse_fwf_dict(st.session_state.standardized_dict)
            st.session_state.colnames = colnames
            st.session_state.colspecs = colspecs

            st.success("Fixed width file parsed successfully!")

            st.write("**Column Names:**")
            st.write(colnames)

            st.write("**Column Specifications:**")
            st.write(colspecs)

        except Exception as e:
            st.error(f"Error parsing fixed width file: {str(e)}")

if st.session_state.standardized_dict is not None:
    st.subheader("Download Options")
    csv = st.session_state.standardized_dict.to_csv(index=False)
    st.download_button(
        label="Download Standardized Dictionary as CSV",
        data=csv,
        file_name="standardized_dictionary.csv",
        mime="text/csv"
    )

show_session_state()