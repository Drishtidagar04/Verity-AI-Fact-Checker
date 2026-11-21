import streamlit as st
import plotly.express as px
import pandas as pd

def style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
    .stApp{background:#0b1020}.block-container{max-width:1420px;padding-top:1.6rem}
    [data-testid="stSidebar"]{background:#0d1426;border-right:1px solid #263550}
    h1,h2,h3{font-family:Manrope,sans-serif;letter-spacing:-.03em}
    .hero{padding:26px 30px;border-radius:18px;background:linear-gradient(115deg,#12203e,#20375f 58%,#392f68);border:1px solid #3a5076;margin-bottom:18px}
    .kicker{font-size:11px;letter-spacing:.15em;color:#9bb9f0;font-weight:700}
    .hero h1{font-size:32px;color:#f6f8ff;margin:8px 0}.hero p{color:#d2def2;font-size:14px}
    div[data-testid="stMetric"]{background:#111a2d;border:1px solid #263550;border-radius:14px;padding:14px}
    div[data-testid="stMetricLabel"] p{color:#a6b6d1;font-size:12px}
    .panel{background:#111a2d;border:1px solid #263550;border-radius:14px;padding:18px}
    .stButton>button[kind="primary"]{background:linear-gradient(90deg,#617df0,#8265d9);border:0;border-radius:10px;font-weight:700}
    div[data-testid="stFileUploader"]{background:#111a2d;border:1px dashed #526b96;border-radius:14px}
    </style>""",unsafe_allow_html=True)

def hero(section,title,desc):
    st.markdown(f'<div class="hero"><div class="kicker">{section}</div><h1>{title}</h1><p>{desc}</p></div>',unsafe_allow_html=True)

def donut(counts):
    data=[(k,v) for k,v in counts.items() if v]
    if not data: st.info("No saved audits yet. Run your first PDF review to populate this chart."); return
    df=pd.DataFrame(data,columns=["Verdict","Claims"])
    fig=px.pie(df,names="Verdict",values="Claims",hole=.68,color="Verdict",
      color_discrete_map={"VERIFIED":"#36c99a","INACCURATE":"#f2b65c","FALSE":"#ef7181",
      "INSUFFICIENT EVIDENCE":"#8494ad","AI REVIEW FAILED":"#e3c56a","SEARCH FAILED":"#a08be8"})
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#e7eefb",
                      legend_title_text="",height=300,margin=dict(l=5,r=5,t=5,b=5))
    st.plotly_chart(fig,use_container_width=True)
