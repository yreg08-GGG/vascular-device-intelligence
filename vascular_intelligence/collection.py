"""PubMed search, retrieval, and XML parsing. No credentials required."""
from dataclasses import dataclass
import time
import threading

import requests
from defusedxml import ElementTree as ET

TOPICS = {
    "Complex aortic aneurysm repair": '(aortic aneurysm[Title/Abstract]) AND (complex[Title/Abstract] OR juxtarenal[Title/Abstract] OR pararenal[Title/Abstract] OR thoracoabdominal[Title/Abstract]) AND (endovascular[Title/Abstract] OR repair[Title/Abstract])',
    "Fenestrated and branched endografts": '(aortic[Title/Abstract]) AND (fenestrated[Title/Abstract] OR branched[Title/Abstract]) AND (endograft*[Title/Abstract] OR endovascular[Title/Abstract])',
    "Thoracic endovascular repair": '(thoracic[Title/Abstract] AND endovascular[Title/Abstract] AND (repair[Title/Abstract] OR aortic[Title/Abstract])) OR TEVAR[Title/Abstract]',
}


@dataclass(frozen=True)
class Publication:
    pmid: str
    title: str
    publication_date: str
    journal: str
    abstract: str

    @property
    def url(self):
        return f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"


def _text(element):
    return "" if element is None else " ".join("".join(element.itertext()).split())


def parse_pubmed_xml(xml):
    """Preserve mixed markup, structured abstracts, and partial publication dates."""
    root = ET.fromstring(xml)
    error = root.find('.//ERROR')
    if error is not None:
        raise ValueError(_text(error))
    publications = []
    for record in root.findall('PubmedArticle'):
        citation = record.find('MedlineCitation')
        article = record.find('MedlineCitation/Article')
        pmid = _text(record.find('MedlineCitation/PMID'))
        if article is None or not pmid.isdigit():
            continue
        date = article.find('Journal/JournalIssue/PubDate')
        parts = [_text(date.find(p)) for p in ('Year', 'Month', 'Day')] if date is not None else []
        publication_date = "-".join(p for p in parts if p)
        if not publication_date and date is not None:
            publication_date = _text(date.find('MedlineDate'))
        if not publication_date:
            electronic = article.find('ArticleDate')
            if electronic is not None:
                publication_date = "-".join(_text(electronic.find(p)) for p in ('Year', 'Month', 'Day') if _text(electronic.find(p)))
        sections = []
        for section in article.findall('Abstract/AbstractText'):
            label = section.get('Label') or section.get('NlmCategory', '')
            body = _text(section)
            if body:
                sections.append(f"{label}: {body}" if label and label != 'UNASSIGNED' else body)
        publications.append(Publication(pmid, _text(article.find('ArticleTitle')) or 'Untitled publication', publication_date, _text(article.find('Journal/Title')) or _text(article.find('Journal/ISOAbbreviation')), '\n\n'.join(sections)))
    return publications


_lock = threading.Lock()
_last_request = 0.0


class PubMedClient:
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

    def _get(self, endpoint, **params):
        global _last_request
        for attempt in range(3):
            # Shared across Streamlit sessions in this process; below 3 requests/sec.
            with _lock:
                time.sleep(max(0, 0.4 - (time.monotonic() - _last_request)))
                _last_request = time.monotonic()
                response = requests.get(self.base_url + endpoint, params={'db': 'pubmed', 'tool': 'vascular_device_intelligence', **params}, timeout=30)
            if response.status_code == 429 or response.status_code >= 500:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
            response.raise_for_status()
            return response
        raise RuntimeError('PubMed request failed')

    def collect(self, topic, limit=50):
        if topic not in TOPICS or not 1 <= limit <= 500:
            raise ValueError('Select a supported topic and a limit between 1 and 500')
        result = self._get('esearch.fcgi', term=TOPICS[topic], retmode='json', retmax=limit, sort='pub date').json()
        if 'error' in result:
            raise ValueError(str(result['error']))
        search = result['esearchresult']
        ids = search['idlist']
        publications = []
        for start in range(0, len(ids), 100):
            xml = self._get('efetch.fcgi', id=','.join(ids[start:start + 100]), retmode='xml').content
            publications.extend(parse_pubmed_xml(xml))
        return publications, int(search['count'])
