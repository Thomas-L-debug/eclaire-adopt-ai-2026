#!/usr/bin/env python3
"""Serve the site and a read-only API over the Neon studies."""

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import psycopg

ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8765


def read_only_url():
    """The site uses the shared read-only address, never .env.local."""
    path = ROOT / ".env"
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"DATABASE_URL est absent de {path}")


def fetch_payload(params):
    query = " ".join(params.get("q", [])).strip()
    results = set(params.get("results", []))

    clauses = []
    values = []
    if query:
        clauses.append("search_vector @@ websearch_to_tsquery('fr', %s)")
        values.append(query)
    if results == {"with"}:
        clauses.append("has_results")
    elif results == {"without"}:
        clauses.append("NOT has_results")

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    if query:
        order = "ts_rank(search_vector, websearch_to_tsquery('fr', %s)) DESC"
        values.append(query)
    else:
        order = "title"

    sql = f"""
        SELECT nct_id, title, has_results, fiche
        FROM studies
        {where}
        ORDER BY {order}
    """

    with psycopg.connect(read_only_url()) as conn:
        rows = conn.execute(sql, values).fetchall()

    studies = []
    for nct_id, title, has_results, fiche in rows:
        if isinstance(fiche, str):
            fiche = json.loads(fiche)
        studies.append({
            "nct_id": nct_id,
            "title": title,
            "has_results": bool(has_results),
            "summary": fiche.get("summary") or "",
            "explain": fiche.get("explain") or "",
            "who": fiche.get("who") or "",
            "participation": fiche.get("participation") or "",
            "participation_steps": fiche.get("participation_steps") or [],
            "where_text": fiche.get("where_text") or "",
            "why": fiche.get("why") or "",
            "results_short": fiche.get("results_short") or "",
            "results_detailed": fiche.get("results_detailed") or "",
            "ask_doctor": fiche.get("ask_doctor") or [],
        })

    return {"studies": studies}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/studies":
            return super().do_GET()
        try:
            payload = fetch_payload(parse_qs(parsed.query))
            body = json.dumps(payload, ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as exc:
            message = f"Lecture impossible : {exc}".encode()
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(message)))
            self.end_headers()
            self.wfile.write(message)


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print("Lecture seule : la base Neon n'est pas modifiée.")
    print(f"Éclaire sur http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
