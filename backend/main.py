import os, tempfile, base64
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pypdf import PdfReader
from openai import OpenAI
from .config import OPENAI_API_KEY, OPENAI_MODEL
from .db import init_db, get_all, create_conversation, add_message, get_conversations, get_messages, search_sources
from .knowledge import retrieve, ingest
from .solver import solve_mechanics
from .advanced_solver import common_solver

SYSTEM="""You are AI Physics Helper, a physics-only research assistant.
Use retrieved sources as evidence. Never invent citations or papers.
If retrieved evidence is insufficient, say so explicitly.
Explain physics step by step, use LaTeX for equations, preserve units,
and for numerical problems show givens, formula, substitution and result.
Answer in the user's language. End with a Sources section using [SOURCE n].
"""

app=FastAPI(title="AI Physics Helper V2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
client=OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

class Ask(BaseModel):
    question:str
    top_k:int=8
    conversation_id:int|None=None

@app.on_event("startup")
def startup(): init_db()

@app.get("/health")
def health(): return {"ok":True,"documents":len(get_all()),"version":"5.0"}

@app.get("/sources")
def sources(): return get_all()

@app.post("/ask")
def ask(body:Ask):
    quick=solve_mechanics(body.question) or common_solver(body.question)
    docs=retrieve(body.question,body.top_k) if client is not None else []
    cid=body.conversation_id
    if cid is None:
        cid=create_conversation(body.question[:80] or "Physics Chat")
    add_message(cid,"user",body.question)
    context=[]
    for i,d in enumerate(docs,1):
        context.append(
            f"[SOURCE {i}]\nTITLE: {d['title']}\nAUTHORS: {d.get('authors','')}\n"
            f"YEAR: {d.get('year','')}\nSOURCE: {d['source']}\nURL: {d.get('url','')}\n"
            f"DOI: {d.get('doi','')}\nTEXT:\n{d['text'][:8000]}"
        )
    prompt="USER QUESTION:\n"+body.question+"\n\nRETRIEVED SOURCES:\n"+"\n\n".join(context)
    if quick:
        prompt += "\n\nDETERMINISTIC SOLVER RESULT (verify and explain it):\n" + str(quick)
    if client is None:
        if quick:
            answer = "الحل الحسابي المحلي:\n" + "\n".join(quick.get("steps", [])) + "\n\nتنبيه: مفتاح OpenAI غير مُعد، لذلك لم يتم تشغيل الشرح الذكي والمصادر."
            add_message(cid,"assistant",answer)
            return {"conversation_id":cid,"answer":answer,"sources":[]}
        raise RuntimeError("OPENAI_API_KEY is not configured")
    r=client.responses.create(model=OPENAI_MODEL,instructions=SYSTEM,input=prompt)
    add_message(cid,"assistant",r.output_text)
    return {"conversation_id":cid,"answer":r.output_text,"sources":[
        {"n":i+1,"title":d["title"],"authors":d.get("authors",""),
         "year":d.get("year"),"source":d["source"],"url":d.get("url",""),"doi":d.get("doi","")}
        for i,d in enumerate(docs)
    ]}

@app.post("/ingest/pdf")
async def ingest_pdf(file:UploadFile=File(...)):
    if Path(file.filename).suffix.lower()!=".pdf":
        return {"error":"Only PDF files are supported"}
    data=await file.read()
    with tempfile.NamedTemporaryFile(suffix=".pdf",delete=False) as f:
        f.write(data); path=f.name
    text="\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
    title=Path(file.filename).stem
    rid=ingest({"title":title,"authors":"","year":None,"source":"user_pdf",
                "url":"","doi":"","abstract":"","text":text})
    return {"ok":True,"id":rid,"title":title}

@app.post("/ingest/arxiv")
def ingest_arxiv(query="cat:physics.*",max_results:int=25):
    from .sources import arxiv
    return {"ingested":arxiv(query,max_results)}

@app.post("/ingest/crossref")
def ingest_crossref(query="physics",max_results:int=20):
    from .sources import crossref
    return {"ingested":crossref(query,max_results)}

@app.post("/ingest/openalex")
def ingest_openalex(query="physics",max_results:int=25):
    from .sources import openalex
    return {"ingested":openalex(query,max_results)}

@app.post("/analyze-image")
async def analyze_image(file: UploadFile=File(...)):
    data=await file.read()
    if client is None:
        return {"error":"OPENAI_API_KEY is not configured"}
    b64=base64.b64encode(data).decode("utf-8")
    mime=file.content_type or "image/jpeg"
    prompt="""Analyze this physics problem image. Read the text and diagrams,
extract givens and units, identify the physical principles, solve step by step,
and state any ambiguity. Answer in Arabic unless the image is clearly in another
language. Do not invent unreadable values."""
    r=client.responses.create(
        model=OPENAI_MODEL,
        instructions=SYSTEM,
        input=[{
            "role":"user",
            "content":[
                {"type":"input_text","text":prompt},
                {"type":"input_image","image_url":f"data:{mime};base64,{b64}"}
            ]
        }]
    )
    return {"answer":r.output_text}

@app.get("/conversations")
def conversations():
    return get_conversations()

@app.get("/conversations/{conversation_id}")
def conversation(conversation_id:int):
    return get_messages(conversation_id)

@app.get("/search")
def search(q:str, category:str|None=None, limit:int=50):
    return search_sources(q,category,limit)


STATIC_DIR=Path(__file__).resolve().parent.parent / "backend_static"
if STATIC_DIR.exists():
    app.mount("/",StaticFiles(directory=str(STATIC_DIR),html=True),name="static")
