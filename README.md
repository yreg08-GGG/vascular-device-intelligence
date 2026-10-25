# Vascular Device Intelligence Platform

A Python Streamlit dashboard for discovering public vascular-device publications from PubMed. It starts with complex aortic aneurysm repair, fenestrated and branched endografts, and thoracic endovascular repair (TEVAR).

For hosting without installing Python on your Mac, see [DEPLOYMENT.md](DEPLOYMENT.md). Streamlit Community Cloud runs the Python app in the cloud; the hosted demo's SQLite library is shared and temporary.

## Setup and run

Python 3.10 or newer is required. From this project folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1
```

Open http://localhost:8501. Select a topic and click **Retrieve from PubMed**. Retrieval requires internet access to `https://eutils.ncbi.nlm.nih.gov`; no API key or credentials are needed. The application makes no external requests until retrieval is requested. Saved records remain browseable offline after restarting.

## Behavior and data

- ESearch selects up to 500 recent matches per retrieval, followed by EFetch XML batches of 100. Each topic's exact search expression is visible in the sidebar. These broad discovery queries can include nonclinical publications; results are not a systematically screened clinical evidence set.
- Saves PMID, title, reported publication date, journal, available abstract, retrieval timestamp, and topic membership to `data/publications.sqlite3`. The directory is created automatically. Repeated retrieval updates records by PMID, retaining topic associations.
- Supports mixed XML text, structured abstracts, missing abstracts, partial dates, seasonal dates, and electronic date fallback. Date precision is preserved. Sorting within a year is approximate where PubMed supplies textual months or seasons.
- Public PubMed links open each source record. No patient-level data, private files, credentials, financial services, payments, or transactions are accessed.
- Requests are spaced at least 0.4 seconds apart across sessions within one application process, with timeouts and bounded retries for HTTP 429/5xx responses. Avoid parallel app processes sharing an IP at high request volume.
- Abstracts may be copyrighted by their publishers; availability through PubMed does not imply unrestricted redistribution.

NCBI API reference: [E-utilities documentation](https://www.ncbi.nlm.nih.gov/books/NBK25499/). This small interactive application uses the public unauthenticated API; for larger deployments review NCBI's tool/contact registration and usage guidance.

## Code structure

```text
app.py                              Streamlit dashboard
vascular_intelligence/collection.py  Topic queries, API client, XML parser
vascular_intelligence/storage.py     SQLite schema, upserts, queries
tests/                              Offline automated tests
```

## Tests

```sh
source .venv/bin/activate
python -m pytest -q
```

Tests cover mixed-content titles, structured abstracts, partial and missing dates, electronic dates, empty/malformed responses, API errors, and SQLite deduplication with overlapping topics. Tests do not contact PubMed.
