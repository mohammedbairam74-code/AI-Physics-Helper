import argparse
from .db import init_db
from .sources import arxiv, openalex, crossref

p=argparse.ArgumentParser(description="AI Physics Helper knowledge ingestion")
p.add_argument("source",choices=["arxiv","openalex","crossref"])
p.add_argument("--query",default="physics")
p.add_argument("--limit",type=int,default=25)
a=p.parse_args()
init_db()
fn={"arxiv":arxiv,"openalex":openalex,"crossref":crossref}[a.source]
print("Ingested:",fn(a.query,a.limit))
