# app.py
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# Autorise ton front (pendant le dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod: mets l'URL exacte de ton front
    allow_methods=["*"],
    allow_headers=["*"],
)

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"

def sparql(query: str) -> dict:
    r = requests.get(
        WIKIDATA_SPARQL,
        params={"query": query, "format": "json"},
        headers={"User-Agent": "4IF-WS-DinoProject/1.0 (contact: you@insa-lyon.fr)"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()

@app.get("/api/dinos")
def list_dinos(limit: int = Query(50, ge=1, le=500)):
    q = f"""
    SELECT ?dino ?dinoLabel ?length WHERE {{
      ?dino wdt:P31 wd:Q23038290;
            wdt:P171 ?parentTaxon;
            wdt:P2348 ?geologicalPeriod;
            wdt:P2043 ?length.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT {limit}
    """
    data = sparql(q)
    rows = []
    for b in data["results"]["bindings"]:
        rows.append({
            "dino": b["dino"]["value"],
            "label": b["dinoLabel"]["value"],
            "length": b["length"]["value"],
        })
    return {"count": len(rows), "items": rows}
