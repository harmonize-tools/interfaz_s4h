import streamlit as st
from streamlit.components.v1 import html
from streamlit_theme import st_theme

def initialize_session_state():
    if 'Data_Sources' not in st.session_state:
        st.session_state.Data_Sources = []
    if 'standardized_dict' not in st.session_state:
        st.session_state.standardized_dict = None
    if "is_fwf" not in st.session_state:
        st.session_state.is_fwf = False
    if "colnames" not in st.session_state:
        st.session_state.colnames = None
    if "colspecs" not in st.session_state:
        st.session_state.colspecs = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def show_session_state():
    st.sidebar.header("Session State")

    if st.session_state.standardized_dict is not None:
        st.sidebar.write("Standardized Dictionary: Loaded" if st.session_state.standardized_dict is not None else "Not Loaded")

    if st.session_state.is_fwf:
        st.sidebar.write("Colnames Loaded" if st.session_state.colnames is not None else "No Colnames Loaded")
        st.sidebar.write("Colspecs Loaded" if st.session_state.colspecs is not None else "No Colspecs Loaded")

    if st.session_state.Data_Sources:
        st.sidebar.write(f"Total databases loaded: {len(st.session_state.Data_Sources)}")
        st.sidebar.subheader("Loaded Data Sources:")
        for i, df in enumerate(st.session_state.Data_Sources):
            st.sidebar.write(f"DataFrame {i + 1} shape: {len(df)} rows, {len(df.columns)} columns")

    #st.session_state.get("messages", []),

def mode(series):
    mode = series.mode()
    if len(mode) > 1:
        return ','.join(mode)
    else:
        return mode.iloc[0]

def add_logo():
    theme = st_theme()
    if theme is not None and theme.get('base') == 'dark':
        logo_url = "https://raw.githubusercontent.com/harmonize-tools/interfaz_s4h/main/assets/logo_alt.png"
    else:
        logo_url = "https://raw.githubusercontent.com/harmonize-tools/interfaz_s4h/main/assets/logo.png"
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(""" + logo_url + """);
                background-repeat: no-repeat;
                padding-top: 120px;
                background-size: 184px 67px;
            }
            [data-testid="stSidebarNav"]::before {
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )