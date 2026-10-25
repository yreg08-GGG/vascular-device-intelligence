from vascular_intelligence.collection import Publication
from vascular_intelligence.storage import save_publications, load_publications


def test_upsert_and_overlapping_topics(tmp_path):
    db = tmp_path / 'library.sqlite3'
    p = Publication('123', 'Aortic repair', '2024', 'Journal', '')
    save_publications([p, p], 'A', db)
    save_publications([Publication('123', 'Updated title', '2025', 'Journal', 'Abstract')], 'B', db)
    assert len(load_publications(db=db)) == 1
    assert load_publications('A', db)[0]['title'] == 'Updated title'
    assert len(load_publications('B', db)) == 1
    assert load_publications('unknown', db) == []
