import pytest
from vascular_intelligence.collection import parse_pubmed_xml


def article(body, pmid='123'):
    return f'<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>{pmid}</PMID><Article>{body}</Article></MedlineCitation></PubmedArticle></PubmedArticleSet>'


def test_mixed_content_and_structured_abstract():
    records = parse_pubmed_xml(article('''<ArticleTitle>Branched <i>aortic</i> repair</ArticleTitle>
        <Journal><Title>Vascular Journal</Title><JournalIssue><PubDate><Year>2025</Year><Month>03</Month><Day>02</Day></PubDate></JournalIssue></Journal>
        <Abstract><AbstractText Label="METHODS">A <b>prospective</b> study.</AbstractText><AbstractText Label="RESULTS">Good outcomes.</AbstractText></Abstract>'''))
    p = records[0]
    assert p.title == 'Branched aortic repair'
    assert p.publication_date == '2025-03-02'
    assert p.journal == 'Vascular Journal'
    assert p.abstract == 'METHODS: A prospective study.\n\nRESULTS: Good outcomes.'
    assert p.url == 'https://pubmed.ncbi.nlm.nih.gov/123/'


@pytest.mark.parametrize('date,expected', [('<Year>2024</Year>', '2024'), ('<MedlineDate>2023 Winter</MedlineDate>', '2023 Winter'), ('', '')])
def test_partial_dates_and_missing_metadata(date, expected):
    p = parse_pubmed_xml(article(f'<Journal><JournalIssue><PubDate>{date}</PubDate></JournalIssue></Journal>'))[0]
    assert p.publication_date == expected
    assert p.abstract == ''
    assert p.title == 'Untitled publication'


def test_electronic_date_fallback():
    p = parse_pubmed_xml(article('<ArticleDate><Year>2022</Year><Month>06</Month></ArticleDate>'))[0]
    assert p.publication_date == '2022-06'


def test_empty_and_invalid_records():
    assert parse_pubmed_xml('<PubmedArticleSet/>') == []
    assert parse_pubmed_xml(article('', pmid='bad')) == []


def test_malformed_and_api_errors():
    with pytest.raises(Exception):
        parse_pubmed_xml('<broken')
    with pytest.raises(ValueError, match='Unavailable'):
        parse_pubmed_xml('<eFetchResult><ERROR>Unavailable</ERROR></eFetchResult>')
