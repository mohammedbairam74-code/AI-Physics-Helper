SOURCE_WEIGHTS = {
    "arXiv": 1.00,
    "OpenAlex": 0.92,
    "Crossref": 0.88,
    "user_pdf": 0.85
}

def quality_score(doc, similarity):
    return float(similarity) * SOURCE_WEIGHTS.get(doc.get("source",""),0.75)
