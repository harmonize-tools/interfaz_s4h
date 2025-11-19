import streamlit as st
import pandas as pd
import numpy as np
import io
import contextlib
import traceback
import builtins

from utils import initialize_session_state, show_session_state, add_logo


st.set_page_config(page_title="Visualization Playground", page_icon="assets/s4h.ico", layout="wide")
add_logo()

initialize_session_state()

st.title("Visualization Playground 🧪")

with st.expander("Quick guide (for beginners)", expanded=True):
    st.markdown(
        """
        This small playground lets you run short Python snippets inside the app.

        - Safe-ish: the runner restricts builtins to a small list and only exposes `pd` (pandas), `np` (numpy), `st` (streamlit),
          `session` (session state) and `dataframes` (the list of loaded datasets) to your code.
        - How to use:
          1) Pick or paste a short snippet on the left.
          2) Click "Run code". Output (print) and exceptions appear below.
          3) If your code produces a pandas DataFrame and assigns it to a variable named `result`, you'll be able to preview and download it.

        Helpful tip: try `df = dataframes[0]` to access the first loaded dataset (if any), then `result = df.head()` to preview.

        Warning: This is not a full security sandbox. Don't run untrusted code on a shared server.
        """
    )


col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("Code editor")

    samples = {
        "Show first loaded dataset": "# Access the first dataset in session (if available)\nif dataframes:\n    df = dataframes[0]\n    result = df.head()\n    print('Loaded dataframe with', len(df), 'rows and', len(df.columns), 'columns')\nelse:\n    print('No datasets loaded in session.')\n",
        "Simple plot": '''# Simple plot: distribution of a column from the first loaded dataset
if dataframes:
    df = dataframes[0]
    # prefer P110D, otherwise first available column
    col = 'P110D' if 'P110D' in df.columns else (df.columns[0] if len(df.columns) > 0 else None)
    if col:
        counts = df[col].fillna('Missing').astype(str).value_counts()
        if hasattr(counts, 'compute'):
            counts = counts.compute()
        st.write('Distribution of ' + str(col) + ':')
        st.bar_chart(counts)
        result = counts.reset_index().rename(columns={'index': col, 0: 'count'})
    else:
        print('No columns found in the first loaded dataset')
else:
    print('No datasets loaded in session.')
''',
    }

    sample_key = st.selectbox("Load sample", options=list(samples.keys()))
    code_default = samples[sample_key]

    code = st.text_area("Type Python code here", value=code_default, height=240, key="playground_code")

    run = st.button("Run code")

with col2:
    st.subheader("Output")
    output_area = st.empty()
    result_preview = st.empty()


def make_safe_builtins():
    allowed = [
        'abs', 'min', 'max', 'sum', 'len', 'range', 'print', 'list', 'dict', 'set', 'tuple',
        'float', 'int', 'str', 'bool', 'enumerate', 'zip', 'map', 'filter', 'hasattr', 'getattr'
    ]
    safe = {}
    for name in allowed:
        if hasattr(builtins, name):
            safe[name] = getattr(builtins, name)
    return safe


if run:
    # Prepare execution environment
    exec_globals = {}
    exec_globals['pd'] = pd
    exec_globals['np'] = np
    exec_globals['st'] = st
    exec_globals['session'] = st.session_state
    exec_globals['dataframes'] = st.session_state.get('Data_Sources', [])

    # Restrict builtins
    exec_globals['__builtins__'] = make_safe_builtins()

    stdout = io.StringIO()
    stderr = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            # Execute user code
            exec(code, exec_globals)

    except Exception:
        tb = traceback.format_exc()
        stderr.write(tb)

    out_text = stdout.getvalue()
    err_text = stderr.getvalue()

    if out_text:
        output_area.code(out_text, language='text')
    else:
        output_area.info("(No printed output)")

    if err_text:
        st.error("Error while executing code:")
        st.code(err_text)

    # If user created a variable named `result`, show a preview/download if it's a DataFrame
    if 'result' in exec_globals and isinstance(exec_globals['result'], pd.DataFrame):
        df_res = exec_globals['result']
        result_preview.markdown("**Result (pandas DataFrame preview):**")
        result_preview.dataframe(df_res.head())

        try:
            csv = df_res.to_csv(index=False)
            st.download_button(label="Download result as CSV", data=csv, file_name="playground_result.csv", mime="text/csv")
        except Exception as e:
            st.warning(f"Could not prepare CSV download: {e}")
    else:
        # show names of created variables (small sample)
        created = [k for k in exec_globals.keys() if k not in ('pd', 'np', 'st', 'session', 'dataframes', '__builtins__')]
        if created:
            st.write("Created variables:", ', '.join(created))


show_session_state()
