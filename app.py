"""Streamlit dashboard. Run: python -m streamlit run app.py."""
import streamlit as st
from vascular_intelligence.collection import PubMedClient, TOPICS
from vascular_intelligence.storage import load_publications, save_publications

st.set_page_config(page_title='Vascular Device Intelligence Platform', page_icon='🩺', layout='wide')
st.title('Vascular Device Intelligence Platform')
st.caption('Public clinical literature • PubMed / NCBI • Local SQLite library')

with st.sidebar:
    st.header('Collect publications')
    topic = st.selectbox('Clinical focus', list(TOPICS))
    limit = st.slider('Most recent records to retrieve', 10, 500, 50, 10)
    with st.expander('PubMed search query'):
        st.code(TOPICS[topic], language=None)
    if st.button('Retrieve from PubMed', type='primary'):
        try:
            with st.spinner('Searching PubMed and saving publication metadata…'):
                records, total = PubMedClient().collect(topic, limit)
                save_publications(records, topic)
            st.success(f'Saved {len(records)} records from {total:,} PubMed matches.')
        except Exception as exc:
            st.error(f'Retrieval failed. Existing saved records are available. {exc}')
    st.caption('Retrieval is manual. No API key or credentials are used.')

scope = st.selectbox('Browse saved publications', ['All topics', *TOPICS])
search = st.text_input('Search saved titles, journals, and abstracts')
try:
    rows = load_publications(None if scope == 'All topics' else scope)
except Exception as exc:
    st.error(f'Cannot read the local database: {exc}')
    st.stop()
library_count = len(rows)
if search:
    rows = [r for r in rows if search.casefold() in ' '.join(r[k] or '' for k in ('title', 'journal', 'abstract')).casefold()]
a, b, c = st.columns(3)
a.metric('Saved in selected scope', library_count)
b.metric('Matching publications', len(rows))
c.metric('With abstracts', sum(bool(r['abstract']) for r in rows))
st.caption('Dates retain PubMed precision (year, month, day, or season). Sorted by reported publication year and date text; within-year order can be approximate.')
if not rows:
    st.info('No matching saved publications. Retrieve a clinical topic from the sidebar or change your search.')
for row in rows:
    with st.container(border=True):
        st.subheader(row['title'])
        st.write(f"{row['journal'] or 'Journal unavailable'} · {row['publication_date'] or 'Date unavailable'} · PMID {row['pmid']}")
        st.link_button('View on PubMed ↗', f"https://pubmed.ncbi.nlm.nih.gov/{row['pmid']}/")
        with st.expander('Abstract'):
            st.text(row['abstract'] or 'No abstract available in PubMed.')
        st.caption(f"Last retrieved (UTC): {row['fetched_at']}")
st.caption('Literature discovery only. Search results are not a systematic review or an assessment of clinical evidence quality.')
