import json, sqlite3
from pathlib import Path
from datetime import datetime,timezone
from app.config import DB_PATH

def db():
    Path(DB_PATH).parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c

def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS audits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,filename TEXT,created_at TEXT,page_count INTEGER,
        claims_found INTEGER,filtered_candidates INTEGER,summary_json TEXT,findings_json TEXT)""")

def summary(findings):
    keys=["VERIFIED","INACCURATE","FALSE","INSUFFICIENT EVIDENCE","AI REVIEW FAILED","SEARCH FAILED"]
    return {k:sum(1 for x in findings if x["result"].get("verdict")==k) for k in keys}

def save_audit(filename,audit):
    created=datetime.now(timezone.utc).isoformat(); findings=audit["findings"]; counts=summary(findings)
    with db() as c:
        cur=c.execute("INSERT INTO audits(filename,created_at,page_count,claims_found,filtered_candidates,summary_json,findings_json) VALUES(?,?,?,?,?,?,?)",
        (filename,created,audit["page_count"],audit["claims_found"],audit["filtered_candidates"],json.dumps(counts),json.dumps(findings)))
        return cur.lastrowid

def list_audits():
    with db() as c: return [dict(x) for x in c.execute("SELECT * FROM audits ORDER BY id DESC").fetchall()]

def get_audit(aid):
    with db() as c: row=c.execute("SELECT * FROM audits WHERE id=?",(aid,)).fetchone()
    if not row:return None
    d=dict(row); d["summary"]=json.loads(d.pop("summary_json")); d["findings"]=json.loads(d.pop("findings_json")); return d

def delete_audit(aid):
    with db() as c: c.execute("DELETE FROM audits WHERE id=?",(aid,))

def totals(rows):
    from collections import Counter
    result=Counter()
    for r in rows: result.update(json.loads(r["summary_json"]))
    return dict(result)
