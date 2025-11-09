"""Home page for the socio4health Streamlit interface.

This page presents the package overview, features, and target users.
Replaced previous content with a clear, emoji-free description.
"""

import streamlit as st


st.set_page_config(page_title="socio4health", page_icon=None, layout="wide")


def main():
    st.title("socio4health")

    st.header("Introduction")
    st.markdown(
        """
        The Python package socio4health is an extraction, transformation, and loading tool
        designed to simplify the process of collecting and merging data from multiple
        sources into a unified database structure.
        """
    )

    st.header("Features")

    st.subheader("Extraction")
    st.markdown(
        """
        - Retrieve data from online sources using web scraping and from local files.
        - Support for multiple file formats: .csv, .xlsx, .xls, .txt, .sav, and compressed files.
        """
    )

    st.subheader("Transformation")
    st.markdown(
        """
        - Consolidate extracted data into Dask DataFrames for scalable processing.
        - Optimize processing for large files via parallelism and efficient data structures.
        - Manage inconsistencies and discrepancies with anomaly-detection strategies.
        """
    )

    st.subheader("Load")
    st.markdown(
        """
        - Consolidate transformed data into a cohesive database or dataset ready for analysis.
        - Provide options to export to common formats or write directly to supported databases.
        """
    )

    st.subheader("Query")
    st.markdown(
        """
        - Run precise queries and apply transformations to extract the subsets you need.
        - Support natural-language style queries or programmatic filters to simplify access.
        """
    )

    st.header("Who should use socio4health?")
    st.markdown(
        """
        socio4health is ideal for data analysts, scientists, and researchers who frequently
        handle large volumes of data from varied sources and want a streamlined way to
        consolidate, query, and visualize their data. It is also useful for developers building
        integrations of disparate datasets, and for business intelligence professionals who
        need to generate actionable insights.

        In short, anyone looking to simplify data workflows from extraction to visualization
        and leverage AI-assisted querying will benefit from socio4health.
        """
    )

    st.markdown("---")
    st.markdown("© 2025 socio4health")


if __name__ == "__main__":
    main()