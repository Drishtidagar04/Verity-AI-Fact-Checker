import io, json, re
from pypdf import PdfReader
from app.services.providers import groq_json, tavily_search, ProviderError

INSTRUCTIONS=re.compile(r"\b(must|should|please|submit|submission|deliverables?|evaluation criteria|the task|the objective|the system must|the application must|will be required|click|upload|build a|create a|design a|provide a|share a|the assignment|the assessment|proposed roadmap)\b",re.I)

def extract_pdf(file_obj):
    reader=PdfReader(file_obj); pages=[]
    for i,p in enumerate(reader.pages,1):
        t=p.extract_text() or ""
        if t.strip(): pages.append({"page":i,"text":t})
    return pages,len(reader.pages)

def extract_claims(pages,key,model,max_claims=3):
    txt="\n\n".join(f"[Page {p['page']}]\n{p['text']}" for p in pages)
    system=("Extract only atomic, independently verifiable real-world facts. Exclude instructions, requirements, "
            "opinions, recommendations and future plans. Preserve exact numbers, units, dates and scope. JSON only.")
    prompt=f"""Extract at most {max_claims} factual claims. Prioritize stats, dates, financial/technical figures.
Do not extract what a student, team, product or app must do.
Return {{"claims":[{{"claim":"...","excerpt":"...","page":1,"claim_type":"statistic|date|financial|technical|other"}}]}}.
If none, return empty claims. PDF TEXT:\n{txt[:10000]}"""
    rows=groq_json(prompt,key,model,system,1000).get("claims",[])
    claims=[]; seen=set(); excluded=0
    for x in rows if isinstance(rows,list) else []:
        if not isinstance(x,dict) or not str(x.get("claim","")).strip(): excluded+=1; continue
        claim=str(x["claim"]).strip(); excerpt=str(x.get("excerpt",""))[:350]
        if INSTRUCTIONS.search(claim+" "+excerpt): excluded+=1; continue
        norm=re.sub(r"\W+"," ",claim.lower()).strip()
        if norm in seen: excluded+=1; continue
        seen.add(norm)
        claims.append({"claim":claim,"excerpt":excerpt,"page":int(x.get("page",1)) if str(x.get("page",1)).isdigit() else 1,
                       "claim_type":str(x.get("claim_type","other"))})
    return claims[:max_claims],excluded

def assess_evidence(claim,evidence,key,model):
    system="Conservative fact-checker. Use only provided evidence; never invent facts, corrections or URLs. JSON only."
    ev=[{"title":e["title"][:90],"url":e["url"],"source_type":e["source_type"],"snippet":e["snippet"][:320]} for e in evidence[:2]]
    prompt=f"""Assess this claim against supplied live evidence.
CLAIM: {claim['claim']}
TYPE: {claim['claim_type']}
PDF EXCERPT: {claim['excerpt'][:160]}
EVIDENCE: {json.dumps(ev,ensure_ascii=False)}
VERIFIED=directly supported. INACCURATE=outdated/materially imprecise. FALSE=directly contradicted.
INSUFFICIENT EVIDENCE=missing, weak, unrelated or ambiguous. No search result is not proof of falsity.
Match units, dates, geography and scope. Correct only when evidence supports it.
Return {{"verdict":"VERIFIED|INACCURATE|FALSE|INSUFFICIENT EVIDENCE","confidence":0,
"explanation":"...","corrected_fact":"","evidence_quality":"HIGH|MEDIUM|LOW","used_urls":[]}}"""
    d=groq_json(prompt,key,model,system,1200)
    allowed={"VERIFIED","INACCURATE","FALSE","INSUFFICIENT EVIDENCE"}
    verdict=d.get("verdict") if d.get("verdict") in allowed else "INSUFFICIENT EVIDENCE"
    valid={e["url"] for e in evidence}
    try: conf=max(0,min(100,int(d.get("confidence",0))))
    except: conf=0
    if not evidence: verdict="INSUFFICIENT EVIDENCE"; conf=min(conf,20)
    quality=d.get("evidence_quality","LOW")
    if quality not in {"HIGH","MEDIUM","LOW"}: quality="LOW"
    return {"verdict":verdict,"confidence":conf,"explanation":str(d.get("explanation","")),
            "corrected_fact":str(d.get("corrected_fact","")),"evidence_quality":quality if evidence else "LOW",
            "used_urls":[u for u in d.get("used_urls",[]) if u in valid]}

def run_audit(file_obj,groq_key,tavily_key,model,max_claims=3,progress=None):
    pages,page_count=extract_pdf(file_obj)
    if not any(p["text"].strip() for p in pages): raise ValueError("No selectable PDF text. Scanned PDFs require OCR.")
    claims,excluded=extract_claims(pages,groq_key,model,max_claims)
    findings=[]
    for i,claim in enumerate(claims,1):
        item={"claim":claim,"result":{"verdict":"AI REVIEW FAILED","confidence":0,"explanation":"Review not completed.",
              "corrected_fact":"","evidence_quality":"NOT REVIEWED","used_urls":[],"evidence":[]}}
        try:
            evidence=tavily_search(claim["claim"],tavily_key,2)
            item["result"]["evidence"]=evidence  # persist before model call
            try:
                result=assess_evidence(claim,evidence,groq_key,model)
                result["evidence"]=evidence
                item["result"]=result
            except ProviderError as e:
                item["result"]["verdict"]="AI REVIEW FAILED"
                item["result"]["explanation"]=str(e)
        except ProviderError as e:
            item["result"]["verdict"]="SEARCH FAILED"; item["result"]["explanation"]=str(e)
        except Exception as e:
            item["result"]["verdict"]="SEARCH FAILED"; item["result"]["explanation"]=str(e)
        findings.append(item)
        if progress: progress(i,len(claims))
    return {"page_count":page_count,"claims_found":len(claims),"filtered_candidates":excluded,"findings":findings}
