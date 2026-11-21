
import streamlit as st
import plotly.express as px
import pandas as pd


def style():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

        /* Main application background */
        .stApp,
        [data-testid="stAppViewContainer"] {
            background: #0b1020 !important;
            color: #ffffff !important;
            font-family: 'DM Sans', sans-serif !important;
        }

        .block-container {
            max-width: 1420px;
            padding-top: 1.6rem;
        }

        /* Top Streamlit header */
        header[data-testid="stHeader"],
        [data-testid="stHeader"],
        .stAppHeader {
            background: #0b1020 !important;
            color: #ffffff !important;
        }

        [data-testid="stToolbar"] {
            background: #0b1020 !important;
        }

        [data-testid="stDecoration"] {
            background: #6366f1 !important;
        }

        /* Headings */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
            font-family: 'Manrope', sans-serif !important;
            letter-spacing: -0.03em;
        }

        /* General text */
        p, li, label, span, small,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] p {
            color: #f1f5f9;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: #0d1426 !important;
            border-right: 1px solid #263550 !important;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #ffffff !important;
        }

        /* Hero section */
        .hero {
            padding: 26px 30px;
            border-radius: 18px;
            background: linear-gradient(
                115deg,
                #1e1b4b,
                #312e81 58%,
                #4338ca
            );
            border: 1px solid #6366f1;
            margin-bottom: 18px;
        }

        .kicker {
            font-size: 11px;
            letter-spacing: 0.15em;
            color: #c7d2fe !important;
            font-weight: 700;
        }

        .hero h1 {
            font-size: 32px;
            color: #ffffff !important;
            margin: 8px 0;
        }

        .hero p {
            color: #e2e8f0 !important;
            font-size: 14px;
        }

        /* Metric cards */
        div[data-testid="stMetric"] {
            background: #111a2d !important;
            border: 1px solid #263550 !important;
            border-radius: 14px;
            padding: 14px;
        }

        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] p {
            color: #cbd5e1 !important;
            font-size: 13px;
        }

        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {
            color: #ffffff !important;
        }

        div[data-testid="stMetricDelta"],
        div[data-testid="stMetricDelta"] * {
            color: #cbd5e1 !important;
        }

        /* Panels */
        .panel {
            background: #111a2d;
            border: 1px solid #263550;
            border-radius: 14px;
            padding: 18px;
            color: #ffffff !important;
        }

        /* Buttons */
        .stButton > button {
            color: #ffffff !important;
            border: 1px solid #526b96 !important;
            border-radius: 10px;
            font-weight: 600;
            background: #17243d !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(
                90deg, #617df0, #8265d9
            ) !important;
            border: 0 !important;
            border-radius: 10px;
            color: #ffffff !important;
            font-weight: 700;
        }

        /* PDF uploader */
        div[data-testid="stFileUploader"] {
            background: #111a2d !important;
            border: 1px dashed #6366f1 !important;
            border-radius: 14px;
            color: #ffffff !important;
            padding: 8px;
        }

        div[data-testid="stFileUploader"] section {
            background: #111a2d !important;
        }

        div[data-testid="stFileUploaderDropzone"] {
            background: #17243d !important;
            border: 1px dashed #6366f1 !important;
            border-radius: 12px !important;
        }

        div[data-testid="stFileUploader"] * {
            color: #ffffff !important;
        }

        div[data-testid="stFileUploaderDropzone"] button {
            background: #312e81 !important;
            color: #ffffff !important;
            border: 1px solid #6366f1 !important;
        }

        /* Inputs */
        input, textarea {
            color: #ffffff !important;
            background-color: #111a2d !important;
        }

        [data-baseweb="select"] * {
            color: #ffffff !important;
        }

        /* Expanders */
        [data-testid="stExpander"] {
            background: #111a2d !important;
            border: 1px solid #263550 !important;
            border-radius: 12px;
            color: #ffffff !important;
        }

        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] summary p {
            color: #ffffff !important;
        }

        /* Tabs */
        button[data-baseweb="tab"] {
            color: #cbd5e1 !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #ffffff !important;
        }

        /* Captions */
        [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] * {
            color: #cbd5e1 !important;
        }

        /* Links */
        a {
            color: #93b4ff !important;
        }

        /* Alerts */
        [data-testid="stAlert"],
        [data-testid="stAlert"] p {
            color: #ffffff !important;
        }

        /* Dataframes */
        [data-testid="stDataFrame"] {
            color: #ffffff !important;
        }

        /* Dividers */
        hr {
            border-color: #263550 !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


def hero(section, title, desc):
    st.markdown(
        f"""
        <div class="hero">
            <div class="kicker">{section}</div>
            <h1>{title}</h1>
            <p>{desc}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def donut(counts):
    data = [(k, v) for k, v in counts.items() if v]

    if not data:
        st.info(
            "No saved audits yet. Run your first PDF review "
            "to populate this chart."
        )
        return

    df = pd.DataFrame(data, columns=["Verdict", "Claims"])

    fig = px.pie(
        df,
        names="Verdict",
        values="Claims",
        hole=0.68,
        color="Verdict",
        color_discrete_map={
            "VERIFIED": "#36c99a",
            "INACCURATE": "#f2b65c",
            "FALSE": "#ef7181",
            "INSUFFICIENT EVIDENCE": "#8494ad",
            "AI REVIEW FAILED": "#e3c56a",
            "SEARCH FAILED": "#a08be8"
        }
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#ffffff",
            size=12
        ),
        legend=dict(
            title_text="",
            font=dict(
                color="#ffffff",
                size=12
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        height=300,
        margin=dict(l=5, r=5, t=5, b=5)
    )

    fig.update_traces(
        textfont=dict(color="#0b1020")
    )

    st.plotly_chart(fig, use_container_width=True)
