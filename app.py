import os,io,json,time
import streamlit as st
from dotenv import load_dotenv
from app.config import APP_VERSION,DEFAULT_MODEL,MAX_UPLOAD_MB
from app.services.database import init_db,save_audit,list_audits,get_audit,delete_audit,totals,summary
from app.services.factcheck import run_audit
from app.components.ui import style,hero,donut

load_dotenv()
st.set_page_config(page_title="Verity | Evidence Intelligence",page_icon="✦",layout="wide")
style(); init_db()

def secret(k):
    try:
        v=st.secrets.get(k,"")
        if v:return str(v)
    except Exception:pass
    return os.getenv(k,"")

for k in ["groq_key","tavily_key"]:
    if k not in st.session_state: st.session_state[k]=secret("GROQ_API_KEY" if k=="groq_key" else "TAVILY_API_KEY")

with st.sidebar:
    st.markdown("## ✦ VERITY")
    st.caption("EVIDENCE INTELLIGENCE")
    page=st.radio("WORKSPACE",["Overview","New audit","Audit history","Analytics","Product strategy","Settings"],label_visibility="collapsed")
    st.divider()
    st.caption("Groq · "+("Connected key" if st.session_state.groq_key else "Not configured"))
    st.caption("Tavily · "+("Connected key" if st.session_state.tavily_key else "Not configured"))
    st.caption("v"+APP_VERSION)

rows=list_audits(); counts=totals(rows)
keys=["VERIFIED","INACCURATE","FALSE","INSUFFICIENT EVIDENCE","AI REVIEW FAILED","SEARCH FAILED"]
counts={k:counts.get(k,0) for k in keys}

if page=="Overview":
    hero("VERITY / EVIDENCE INTELLIGENCE","Know what your content claims.","A review workspace that extracts factual claims from PDFs, checks live sources and keeps evidence attached to every verdict.")
    a,b,c,d=st.columns(4)
    a.metric("Documents audited",len(rows)); b.metric("Claims reviewed",sum(r["claims_found"] for r in rows))
    c.metric("False claims flagged",counts["FALSE"]); d.metric("Technical failures",counts["AI REVIEW FAILED"]+counts["SEARCH FAILED"])
    left,right=st.columns([1.15,.85])
    with left: st.markdown("### Verdict distribution"); donut(counts)
    with right:
        st.markdown("### The review workflow")
        st.markdown('<div class="panel"><b>01 · Extract</b><p>Identify factual claims and page references.</p><b>02 · Investigate</b><p>Retrieve live web evidence and source links.</p><b>03 · Assess</b><p>Explain each verdict; keep uncertainty explicit.</p><b>04 · Report</b><p>Save an audit trail and export findings.</p></div>',unsafe_allow_html=True)
    st.markdown("### Recent audits")
    if rows: st.dataframe([{"Document":r["filename"],"Created":r["created_at"][:19],"Claims":r["claims_found"]} for r in rows[:7]],use_container_width=True,hide_index=True)
    else: st.info("No audit history yet. Start with New audit.")

elif page=="New audit":
    hero("WORKSPACE / NEW AUDIT","Review a document before it ships.","Upload a text-based PDF. Verity extracts a small set of factual claims, searches live sources and records evidence-backed findings.")
    x,y=st.columns(2)
    with x: model=st.selectbox("Groq model",["openai/gpt-oss-20b","openai/gpt-oss-120b"],index=0)
    with y: max_claims=st.slider("Claims per audit",1,5,3)
    upload=st.file_uploader("Drop your PDF here",type=["pdf"])
    if upload:
        st.success(f"{upload.name} · {upload.size/1024:.1f} KB")
        if upload.size>MAX_UPLOAD_MB*1024*1024: st.error(f"Maximum upload size is {MAX_UPLOAD_MB} MB.")
        elif st.button("Run evidence review",type="primary",use_container_width=True):
            if not st.session_state.groq_key or not st.session_state.tavily_key: st.error("Add Groq and Tavily keys in Settings.")
            else:
                bar=st.progress(0); msg=st.empty()
                def progress(i,n): bar.progress(i/n if n else 1); msg.caption(f"Reviewed {i}/{n} claims")
                try:
                    audit=run_audit(io.BytesIO(upload.getvalue()),st.session_state.groq_key,st.session_state.tavily_key,model,max_claims,progress)
                    aid=save_audit(upload.name,audit)
                    st.session_state["latest_audit"]=aid
                    st.success(f"Audit saved · #{aid}")
                    st.rerun()
                except Exception as e: st.error(f"Could not start audit: {e}")
    st.caption("One extraction call; then one search and one compact assessment call per claim. Provider quotas still apply.")

elif page=="Audit history":
    hero("WORKSPACE / HISTORY","Every review, traceable.","Reopen claim-level evidence and download previous audit reports.")
    query=st.text_input("Search document names")
    for r in [x for x in rows if query.lower() in x["filename"].lower()]:
        with st.container(border=True):
            l,m,n=st.columns([3,1,1])
            l.markdown(f"**{r['filename']}**"); l.caption(f"Audit #{r['id']} · {r['created_at'][:19]}")
            m.metric("Claims",r["claims_found"])
            if n.button("Open",key=f"open{r['id']}"): st.session_state["open_audit"]=r["id"]
            if n.button("Delete",key=f"del{r['id']}"): st.session_state["confirm_delete"]=r["id"]
    if st.session_state.get("confirm_delete"):
        aid=st.session_state["confirm_delete"]; st.warning(f"Delete audit #{aid}?")
        u,v=st.columns(2)
        if u.button("Confirm delete"): delete_audit(aid); st.session_state.pop("confirm_delete",None); st.rerun()
        if v.button("Cancel"): st.session_state.pop("confirm_delete",None); st.rerun()
    aid=st.session_state.get("open_audit")
    if aid:
        report=get_audit(aid)
        if report:
            st.divider(); st.subheader(report["filename"])
            st.download_button("Download JSON",json.dumps(report,indent=2,ensure_ascii=False),f"verity_{aid}.json","application/json")
            for i,item in enumerate(report["findings"],1):
                r=item["result"]
                with st.expander(f"{i}. {r['verdict']} — {item['claim']['claim']}"):
                    st.write(r["explanation"])
                    for e in r.get("evidence",[]): st.markdown(f"- [{e['title'] or e['url']}]({e['url']})")

elif page=="Analytics":
    hero("WORKSPACE / ANALYTICS","Measure review outcomes.","Metrics are calculated only from saved audits. No synthetic activity is included.")
    a,b,c=st.columns(3); a.metric("Audits",len(rows)); b.metric("Claims",sum(r["claims_found"] for r in rows)); c.metric("False verdicts",counts["FALSE"])
    st.markdown("### Verdict mix"); donut(counts)
    st.caption("A verdict count is not a model-accuracy score. Accuracy requires labelled ground-truth examples and human review.")

elif page=="Product strategy":
    hero("PRODUCT / STRATEGY","From detection to defensible action.","Verity supports content, brand and product teams that need an evidence trail before approving claims.")
    st.markdown("""
### Problem and users
Marketing and business PDFs may contain stale statistics, unsupported statements or factual errors. Manual verification is slow. Primary users are content reviewers, product marketers, brand teams and agency strategists.

### Product principles
- Evidence before verdict; every claim links to retrieved sources.
- Uncertainty is valid; missing evidence is not automatically false.
- Explainability: preserve claim, page, source and rationale.
- Human-in-the-loop: reviewers own the final editorial decision.
- Cost-aware processing: configurable small claim limits and explicit provider errors.

### Success metrics
| Metric | Definition |
|---|---|
| Claim extraction yield | Relevant factual claims / extracted candidates |
| Evidence coverage | Claims with relevant evidence / claims reviewed |
| Review completion rate | Audits with terminal status / audits started |
| Median time to review | Time from upload to report |
| Human correction acceptance | Suggested corrections accepted / reviewed |

### Roadmap
**0–3 months:** labelled evaluation set, reviewer feedback, source allowlists, caching, pilot with a small content team.

**3–6 months:** shared workspaces, review assignments, approved-claim library, recurring re-checks and Google Drive/CMS integrations.

**6–12 months:** enterprise SSO, multilingual review, private source allowlists, API/webhooks and managed storage.

### Monetization hypotheses
Free evaluation tier → Team workspace subscription → Business integrations and policy controls → Enterprise governance, SSO, API and deployment options. Pricing requires willingness-to-pay validation; no price point is claimed as validated.
""")

elif page=="Settings":
    hero("WORKSPACE / SETTINGS","Connect your evidence providers.","Keys entered here remain in the current session. For deployment, use Streamlit Secrets.")
    with st.form("keys"):
        g=st.text_input("Groq API key",value=st.session_state.groq_key,type="password")
        t=st.text_input("Tavily API key",value=st.session_state.tavily_key,type="password")
        if st.form_submit_button("Save for this session",type="primary"):
            st.session_state.groq_key=g.strip(); st.session_state.tavily_key=t.strip(); st.success("Keys saved in this session.")
    st.markdown("**Streamlit Cloud Secrets**")
    st.code('GROQ_API_KEY = "your-key"\\nTAVILY_API_KEY = "your-key"',language="toml")
    st.markdown("- [Groq Console](https://console.groq.com/keys)\\n- [Tavily Dashboard](https://app.tavily.com/)")
    st.warning("Never commit .env or API keys. Free-tier access and limits are controlled by providers and can change.")
