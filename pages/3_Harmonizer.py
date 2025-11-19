import tempfile
import io
import zipfile
from pathlib import Path

import streamlit as st
import pandas as pd
from socio4health.utils import harmonizer_utils

from utils import mode, initialize_session_state, show_session_state, add_logo
from socio4health import Harmonizer  # asumiendo que tu clase se llama así

st.set_page_config(page_title="Harmonizer", page_icon="assets/s4h.ico", layout="wide")
add_logo()

initialize_session_state()

st.title("Harmonizer 🎵")

# Beginner-friendly deep guide with image placeholder
with st.expander("Deep guide (easy read for beginners)", expanded=True):
    st.markdown(
        """
        This page helps you make different datasets speak the same language.

        Short overview of the main sections below. Read this first if you are new.

        - Vertical Merge: Combine datasets that have similar columns (one below the other). Use the similarity slider to decide how strict the matching should be.
        - Dictionary Grouping: Automatically group and label variables from the dictionary using a machine learning model. Upload a model (zip) to this section.
        - Data Selector: Filter your datasets by topic (category) and specific values so you only work with relevant rows.
        - Data Joining: Combine datasets side-by-side using a common key column.

        Quick tips:
        1) Always standardize your dictionary first (use the Dictionary Standardization page).
        2) Try higher similarity (closer to 1.0) when column names are already similar; lower it when names vary a lot.
        3) Use the example datasets to practice before using your own files.

        Image: a simple diagram helps a lot. If you place a file named `assets/harmonizer_diagram.png` in the project, it will show below.
        """
    )

    # Image placeholder: show the image if it exists, otherwise display a helpful note
    from pathlib import Path
    img_path = Path("assets/harmonizer_diagram.png")
    if img_path.exists():
        st.image(str(img_path), use_column_width=True, caption="Harmonizer overview")
    else:
        st.info("Add an explanatory diagram at 'assets/harmonizer_diagram.png' to show a visual overview here.")


st.subheader("Vertical Merge")
if not st.session_state.Data_Sources:
    st.warning("⚠️ No data sources loaded. Please upload data first.")
    st.stop()

if st.session_state.standardized_dict is None:
    st.warning("⚠️ No standardized dictionary found. Please standardize a dictionary first.")
    st.stop()

har = Harmonizer()
har.dict_df = st.session_state.standardized_dict

similarity_threshold = st.slider(
    "Similarity Threshold",
    min_value=0.0, max_value=1.0, value=0.9, step=0.05
)

nan_threshold = st.slider(
    "NaN Threshold",
    min_value=0.0, max_value=1.0, value=0.9, step=0.05
)

dfs = st.session_state.Data_Sources

har.similarity_threshold = similarity_threshold
har.nan_threshold = nan_threshold

# Clean NaN columns tool
st.subheader("Clean NaN Columns")
with st.expander("Drop columns with many NaNs (options)", expanded=False):
    st.markdown("Columns where the proportion of missing values is greater than the NaN Threshold will be dropped.")
    use_sampling = st.checkbox("Use sampling for NaN detection (faster for large datasets)")
    sample_frac = None
    if use_sampling:
        sample_frac = st.number_input("Sample fraction (0 < frac <= 1)", min_value=0.01, max_value=1.0, value=0.1, step=0.01)

    if st.button("Drop NaN Columns"):
        # apply settings
        try:
            har.sample_frac = sample_frac
            # run on the session Data_Sources
            with st.spinner("Cleaning columns with many NaNs..."):
                dfs_in = st.session_state.Data_Sources
                cleaned = har.drop_nan_columns(dfs_in)

                # harmonizer returns either a DataFrame or list
                if isinstance(cleaned, list):
                    st.session_state.Data_Sources = cleaned
                else:
                    st.session_state.Data_Sources = [cleaned]

                st.success("Dropped columns with many NaNs")
                st.write("Preview of cleaned datasets:")
                for i, df in enumerate(st.session_state.Data_Sources):
                    try:
                        st.write(f"DataFrame {i + 1} shape: {len(df)} rows, {len(df.columns)} columns")
                        st.dataframe(df.head(5))
                    except Exception:
                        st.write(f"DataFrame {i + 1}: preview not available")

        except Exception as e:
            st.error(f"Error while dropping NaN columns: {e}")

if st.button("Run Vertical Merge"):
    with st.spinner("Running vertical merge..."):
        try:
            merged = har.s4h_vertical_merge(dfs)
            st.session_state.Data_Sources = merged

            st.success("Vertical merge completed!")
            st.write("Preview of merged data:")

            for i, df in enumerate(merged):
                st.write(f"DataFrame {i + 1} shape: {len(df)} rows, {len(df.columns)} columns")
                st.dataframe(df.head(5))

        except Exception as e:
            st.error(f"Error during harmonization: {e}")

st.subheader("Dictionary Grouping")
with st.expander("Dictionary Grouping Options", expanded=False):
    options = har.s4h_get_available_columns(dfs)
    extra_cols = st.multiselect("Extra Columns", options=options)
    har.extra_cols = extra_cols

    st.markdown("**Model (for classification)**")
    model_file = st.file_uploader("Upload model (zip with a model folder inside)", type=["zip"])

    # Button to extract/upload model and remember extracted path in session_state
    if st.button("Upload & Extract Model"):
        if model_file is None:
            st.error("Please choose a model zip file to upload.")
        else:
            # Create models directory in project root and extract the zip
            models_dir = Path("bert_model")
            if models_dir.exists():
                import shutil
                shutil.rmtree(models_dir)
            models_dir.mkdir(exist_ok=True)

            import zipfile
            try:
                with zipfile.ZipFile(model_file, 'r') as zip_ref:
                    zip_ref.extractall(models_dir)

                # Determine actual model folder: if the zip contained a single top-level folder, use it.
                children = [p for p in models_dir.iterdir()]
                model_path = models_dir
                if len(children) == 1 and children[0].is_dir():
                    model_path = children[0]

                st.session_state.bert_model_path = str(model_path)
                st.success(f"Model extracted to {model_path}")
                st.write("Model files:")
                for p in model_path.rglob('*'):
                    st.write('-', str(p.relative_to(model_path)))

            except Exception as e:
                st.error(f"Failed to extract model zip: {e}")

    # Show currently extracted model path if any
    if 'bert_model_path' in st.session_state:
        st.info(f"Using model at: `{st.session_state.bert_model_path}`")

    st.markdown("---")

    # Separate action: Translate dictionary (no model required)
    if st.button("Run Dictionary Translation"):
        with st.spinner("Running dictionary translation..."):
            try:
                dic = st.session_state.standardized_dict
                dic = harmonizer_utils.s4h_translate_column(dic, "question", language="en")
                st.success("Questions translation completed")
                dic = harmonizer_utils.s4h_translate_column(dic, "description", language="en")
                st.success("Descriptions translation completed")
                dic = harmonizer_utils.s4h_translate_column(dic, "possible_answers", language="en")
                st.success("Possible answers translation completed")
                har.dict_df = dic
                st.session_state.standardized_dict = dic

                st.success("Dictionary translation completed")

            except Exception as e:
                st.error(f"Error during dictionary translation: {e}")

    st.markdown("---")

    # Separate action: Classification (requires an extracted model)
    if st.button("Run Dictionary Classification"):
        if 'bert_model_path' not in st.session_state:
            st.error("Please upload and extract a model first using 'Upload & Extract Model'.")
            st.stop()

        model_path = st.session_state.bert_model_path

        with st.spinner("Running dictionary classification..."):
            try:
                dic = st.session_state.standardized_dict

                required_cols = ["question_en", "description_en", "possible_answers_en"]
                missing_cols = [col for col in required_cols if col not in dic.columns]
                if missing_cols:
                    st.error(f"Missing required columns: {', '.join(missing_cols)}")
                    st.stop()

                classified_dic = harmonizer_utils.s4h_classify_rows(
                    dic,
                    "question_en",
                    "description_en",
                    "possible_answers_en",
                    new_column_name="category",
                    MODEL_PATH=model_path
                )

                st.session_state.standardized_dict = classified_dic

                st.success("Dictionary classification completed")
                st.write("Preview of classified dictionary:")
                st.dataframe(classified_dic.head(5))

                # Add a download button so users can save the classified dictionary as CSV
                try:
                    csv = classified_dic.to_csv(index=False)
                    st.download_button(
                        label="Download classified dictionary as CSV",
                        data=csv,
                        file_name="classified_dictionary.csv",
                        mime="text/csv",
                    )
                except Exception:
                    st.warning("Unable to generate CSV for download (unexpected dtype).")

            except Exception as e:
                st.error(f"Error during dictionary classification: {str(e)}")
                raise e

st.subheader("Data Selector")
with st.expander("Data Joining Options", expanded=False):
    category = st.multiselect(
        "Categories",
        options=[
            "Business", "Education", "Fertility", "Housing",
            "Identification", "Migration", "Nonstandard job", "Social Security"
        ],
        default=[
            "Business", "Education", "Fertility", "Housing",
            "Identification", "Migration", "Nonstandard job", "Social Security"
        ]
    )
    # `st.multiselect` returns a list of selected categories; pass it directly.
    har.categories = category
    # Allow null/none selection by adding a 'None' option
    key_col_options = ["None"] + options
    key_col_choice = st.selectbox("Column Selection (optional)", options=key_col_options, index=0)
    har.key_col = None if key_col_choice == "None" else key_col_choice

    key_val_input = st.text_input("Values (comma separated, optional)")
    if key_val_input and key_val_input.strip():
        har.key_val = [v.strip() for v in key_val_input.split(',') if v.strip()]
    else:
        har.key_val = []

    if st.button("Run Data Selector"):
        if not har.categories:
            st.error("Please select at least one category.")
            st.stop()
        # If a key column is provided, require at least one value
        if har.key_col is not None and not har.key_val:
            st.error("Please provide at least one value when a column is selected.")
            st.stop()
        with st.spinner("Running data selector..."):
            try:
                dfs = st.session_state.Data_Sources
                filtered_dask_dfs = har.s4h_data_selector(dfs)
                st.session_state.Data_Sources = filtered_dask_dfs

                st.success("Data selection completed!")
                st.write("Preview of filtered data:")
                for i, df in enumerate(filtered_dask_dfs):
                    st.write(f"DataFrame {i + 1} shape: {len(df)} rows, {len(df.columns)} columns")
                    st.dataframe(df.head(5))

                # Download buttons for each resulting DataFrame and a ZIP of all
                try:
                    for i, df in enumerate(filtered_dask_dfs):
                        try:
                            dfp = df.compute() if hasattr(df, "compute") else df
                            csv_bytes = dfp.to_csv(index=False).encode("utf-8")
                            st.download_button(
                                label=f"Download DataFrame {i+1} as CSV",
                                data=csv_bytes,
                                file_name=f"dataframe_{i+1}.csv",
                                mime="text/csv",
                            )
                        except Exception:
                            st.warning(f"Unable to prepare CSV for DataFrame {i+1}")

                    if len(filtered_dask_dfs) > 1:
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                            for i, df in enumerate(filtered_dask_dfs):
                                try:
                                    dfp = df.compute() if hasattr(df, "compute") else df
                                    csv_data = dfp.to_csv(index=False).encode("utf-8")
                                    zf.writestr(f"dataframe_{i+1}.csv", csv_data)
                                except Exception:
                                    # skip any problematic DF
                                    pass
                        zip_buffer.seek(0)
                        st.download_button(
                            label="Download all DataFrames as zip",
                            data=zip_buffer.getvalue(),
                            file_name="dataframes.zip",
                            mime="application/zip",
                        )
                except Exception as e:
                    st.warning(f"Could not create download buttons: {e}")

            except Exception as e:
                st.error(f"Error during data selection: {e}")


# st.subheader("Data Joining")
# with st.expander("Data Joining Options", expanded=False):
#     # Allow join keys to be optional
#     join_key_options = ["None"] + options
#     join_key_choice = st.selectbox("Join Key", options=join_key_options, index=0)
#     aux_key_choice = st.selectbox("Auxiliar Key (optional)", options=join_key_options, index=0)

#     har.join_key = None if join_key_choice == "None" else join_key_choice
#     har.aux_key = None if aux_key_choice == "None" else aux_key_choice
#     if st.button("Run Data Joining"):
#         if not har.join_key:
#             st.error("Please select a join key.")
#             st.stop()
#         with st.spinner("Running data joining..."):
#             try:
#                 dfs = st.session_state.Data_Sources
#                 joined_dfs = har.s4h_join_data(dfs)
#                 st.session_state.Data_Sources = joined_dfs

#                 st.success("Data joining completed!")
#                 st.write("Preview of joined data:")
#                 for i, df in enumerate(joined_dfs):
#                     st.write(f"DataFrame {i + 1} shape: {len(df)} rows, {len(df.columns)} columns")
#                     st.dataframe(df.head(5))

#             except Exception as e:
#                 st.error(f"Error during data joining: {e}")

show_session_state()

