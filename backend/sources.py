import httpx, feedparser
from .knowledge import ingest

def arxiv(query="cat:physics.*",limit=25):
    r=httpx.get("http://export.arxiv.org/api/query",
        params={"search_query":query,"start":0,"max_results":limit},
        timeout=60)
    r.raise_for_status()
    feed=feedparser.parse(r.text); n=0
    for e in feed.entries:
        ingest({
            "title":e.title.strip(),
            "authors":", ".join(a.name for a in e.authors),
            "year":int(e.published[:4]) if getattr(e,"published","") else None,
            "source":"arXiv","url":e.link,"doi":"","abstract":e.summary,
            "text":e.title+"\n"+e.summary
        }); n+=1
    return n

def openalex(query="physics",limit=25):
    r=httpx.get("https://api.openalex.org/works",
        params={"search":query,"per-page":limit},
        timeout=60)
    r.raise_for_status(); n=0
    for w in r.json().get("results",[]):
        inv=w.get("abstract_inverted_index") or {}
        pairs=[(p,word) for word,pos in inv.items() for p in pos]
        abstract=" ".join(word for _,word in sorted(pairs))
        loc=w.get("primary_location") or {}
        ingest({
            "title":w.get("title") or "Untitled",
            "authors":", ".join((a.get("author") or {}).get("display_name","") for a in w.get("authorships",[])),
            "year":w.get("publication_year"),
            "source":"OpenAlex",
            "url":loc.get("landing_page_url") or w.get("doi") or "",
            "doi":w.get("doi") or "",
            "abstract":abstract,
            "text":(w.get("title") or "")+"\n"+abstract
        }); n+=1
    return n

def crossref(query="physics", limit=20):
    r=httpx.get("https://api.crossref.org/works",
        params={"query.bibliographic":query,"rows":limit,"select":
                "title,author,published,DOI,URL,container-title"},
        headers={"User-Agent":"AI-Physics-Helper/3.0"},
        timeout=60)
    r.raise_for_status()
    n=0
    for w in r.json().get("message",{}).get("items",[]):
        title=(w.get("title") or ["Untitled"])[0]
        authors=", ".join((a.get("given","")+" "+a.get("family","")).strip()
                          for a in w.get("author",[]))
        date=w.get("published",{}).get("date-parts",[[None]])[0]
        year=date[0] if date else None
        url=w.get("URL") or ""
        doi=w.get("DOI") or ""
        ingest({"title":title,"authors":authors,"year":year,
                "source":"Crossref","url":url,"doi":doi,"abstract":"",
                "text":title+"\\n"+authors+"\\n"+(w.get("container-title") or [""])[0]})
        n+=1
    return n
