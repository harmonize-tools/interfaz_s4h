from pathlib import Path

import streamlit as st
import os
import tempfile
from instructions import INSTRUCTIONS
from socio4health import Extractor

from utils import initialize_session_state, show_session_state, add_logo

st.set_page_config(page_title="Data Extraction", page_icon="assets/s4h.ico", layout="wide")
add_logo()

initialize_session_state()

st.title("Data Extraction 📥")

with st.expander("ℹ️ Instructions", expanded=False):
    st.markdown(INSTRUCTIONS["data_loading"])

if 'state' not in st.session_state:
    st.session_state.state = "Select Source"
if 'source_data' not in st.session_state:
    st.session_state.source_data = "Select an Option"

st.session_state.source_data = st.selectbox(
    "Choose data source",
    ["Select an Option", "Internet (URL)", "Local file", "Example Brazil Census 2010", "Example Colombia Housing Survey 2021"],
)


def handle_extraction(extractor, source_type):
    try:
        with st.status(f"🔄 Extracting data from {source_type}...", expanded=True) as status:
            result = extractor.s4h_extract()

            if result:
                status.update(label="✅ Data extraction completed successfully!", state="complete")
                if isinstance(result, list):
                    st.session_state.Data_Sources.extend(result)
                    st.info(f"Added {len(result)} datasets to your workspace")
                else:
                    st.session_state.Data_Sources.append(result)
                    st.info("Added 1 dataset to your workspace")
                return True
            else:
                status.update(label="⚠️ No data extracted", state="error")
                return False

    except Exception as e:
        st.error(f"❌ Error during extraction: {str(e)}")
        return False


def render_csv_options():
    csv_options = st.expander("CSV Options", expanded=False)
    with csv_options:
        sep = st.text_input("Separator", value=",", key="csv_sep")
        encoding = st.selectbox(
            "Encoding",
            ['latin1', 'utf-8', 'iso-8859-1', 'cp1252'],
            key="csv_encoding"
        )
    return sep, encoding

def render_fwf_options():
    is_fwf = st.toggle("Is a fixed width file?")
    colnames = st.session_state.get("colnames", None)
    colspecs = st.session_state.get("colspecs", None)

    if is_fwf:
        if colnames and colspecs:
            st.write("Column Names available:", colnames)
            st.write("Column Specs available:", colspecs)
        else:
            st.info("No column names or specifications found. Please upload and standardize a dictionary first.")
    return is_fwf, colnames, colspecs

def render_extensions(detected_exts = ('.csv', '.zip')):
    extensions = st.multiselect(
        "File extensions to look for",
        ['.csv', '.xls', '.xlsx', '.txt', '.sav', '.zip', '.7z', '.tar', '.gz', '.tgz'],
        default=detected_exts,
        key="extensions"
    )
    return extensions

is_fwf = False

if st.session_state.source_data == "Internet (URL)":
    st.subheader("Enter URLs for datasets")

    col1, col2 = st.columns(2)
    with col1:
        url = st.text_input(
            "Enter URL for Dataset:",
            value="https://microdatos.dane.gov.co/index.php/catalog/663",
            key="url_input"
        )

        extensions = render_extensions()

        if any(ext in ['.txt'] for ext in extensions):
            is_fwf,colnames,colspecs = render_fwf_options()
        else:
            is_fwf = False
            colnames = None
            colspecs = None
        if any(ext in ['.csv', '.txt'] for ext in extensions):
            sep, encoding = render_csv_options()

    with col2:
        key_words = st.text_input(
            "Enter relevant keywords (separated by commas)",
            value="",
            key="keywords"
        )
        depth = st.number_input(
            'Scraping depth',
            min_value=0, max_value=10, value=1, step=1,
            key="depth"
        )

    if st.button("Extract Data from URL"):
        if url and url.strip():
            extractor = Extractor(
                input_path=url,
                down_ext=extensions,
                sep=sep,
                encoding=encoding,
                output_path="./data",
                depth=depth,
                key_words=[kw.strip() for kw in key_words.split(",")] if key_words else None,
                is_fwf = is_fwf,
                colnames = colnames,
                colspecs = colspecs
            )

            # Perform extraction
            if handle_extraction(extractor, "URL"):
                st.session_state.state = "Data Loaded"
                st.rerun()

        else:
            st.warning("Please enter a valid URL")

elif st.session_state.source_data == "Local file":
    st.subheader("Upload local files")


    uploaded_files = st.file_uploader(
        "Choose file",
        type=['csv', 'xlsx', 'xls', 'txt', 'sav', 'zip', '7z', 'tar', 'gz', 'tgz'],
        accept_multiple_files=True,
        key="file_uploader"
    )

    files_extensions = [os.path.splitext(f.name)[1].lower() for f in uploaded_files] if uploaded_files else []
    extensions = files_extensions

    extensions = render_extensions(extensions)

    if any(ext in ['.txt'] for ext in extensions):
        is_fwf, colnames, colspecs = render_fwf_options()
    else:
        is_fwf = False
        colnames = None
        colspecs = None

    sep = ','
    encoding = 'latin1'
    if any(ext in ['.csv'] for ext in extensions):
        sep, encoding = render_csv_options()

    if uploaded_files is not None and st.button("Process Local Files"):
        if 'temp_dir' not in st.session_state:
            st.session_state.temp_dir = tempfile.mkdtemp()

        try:
            for uploaded_file in uploaded_files:
                file_path = Path(st.session_state.temp_dir) / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            extractor = Extractor(
                input_path=st.session_state.temp_dir,
                down_ext=extensions,
                sep=sep,
                output_path="./data",
                encoding=encoding,
                is_fwf=is_fwf,
                colnames=colnames,
                colspecs=colspecs
            )
            dask_dfs = extractor.s4h_extract()
            if dask_dfs:
                if isinstance(dask_dfs, list):
                    st.session_state.Data_Sources.extend(dask_dfs)
                    st.info(f"Added {len(dask_dfs)} datasets to your workspace")
                else:
                    st.session_state.Data_Sources.append(dask_dfs)
                    st.info("Added 1 dataset to your workspace")

                st.success("Data extraction completed successfully!")
                st.session_state.state = "Data Loaded"
                st.rerun()
            else:
                st.error("No data was extracted. Please check your input files.")

        except Exception as e:
            st.error(f"Failed to process {os.path.basename(file_path)}: {str(e)}")

show_session_state()