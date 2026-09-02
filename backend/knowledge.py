import os, json
import numpy as np
from openai import OpenAI
from .config import OPENAI_API_KEY, EMBEDDING_MODEL
from .db import add_document, search_text, get_all
from .ranking import quality_score

client=OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def embed(text):
    if client is None:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    r=client.embeddings.create(model=EMBEDDING_MODEL,input=text[:12000])
    return r.data[0].embedding

def ingest(d):
    d["embedding"]=embed((d.get("title","")+"\n"+d.get("abstract","")+"\n"+d["text"])[:12000])
    return add_document(d)

def retrieve(query,k=8):
    candidates=search_text(query,50)
    if len(candidates)<k:
        candidates=get_all(500)
    q=np.array(embed(query),dtype=np.float32)
    ranked=[]
    for d in candidates:
        if not d.get("embedding"): continue
        v=np.array(json.loads(d["embedding"]),dtype=np.float32)
        den=np.linalg.norm(q)*np.linalg.norm(v)
        sim=float(np.dot(q,v)/den) if den else 0
        ranked.append((quality_score(d,sim),d))
    ranked.sort(key=lambda x:x[0],reverse=True)
    return [d for _,d in ranked[:k]]

def retrieve_with_scores(query,k=8):
    docs=retrieve(query,k)
    return [{"document":d,"score":None} for d in docs]
