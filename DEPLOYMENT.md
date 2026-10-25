# Browser-only deployment with Streamlit Community Cloud

No Python installation is needed on the computer used to visit the hosted app.

1. Sign in to GitHub and create a repository named `vascular-device-intelligence`.
2. Upload the contents of the deployment ZIP into the repository root. Include the `vascular_intelligence` and `.streamlit` directories. Do not upload `.venv` or `data`.
3. Visit https://share.streamlit.io/ and sign in. Review the terms and GitHub authorization yourself, particularly if using an institutional GitHub account.
4. Choose **Create app**, select the repository and branch, and set the entrypoint to `app.py`.
5. In advanced settings, choose Python 3.12. No secrets or API keys are required.
6. Deploy and wait for the build to finish. Streamlit supplies an HTTPS `streamlit.app` URL.
7. Open the URL, retrieve 10 records for one topic, and confirm titles, abstracts, dates, journals, and PubMed links appear. Reload the page and verify the saved records remain available during the running instance.

The source should be in the repository root, not inside an extra enclosing folder. `requirements.txt` installs the runtime dependencies on the server.

## Demo storage limitations

SQLite runs on the hosting server, not in each visitor's browser. All visitors to this demo share its saved publication library. Treat hosted local disk as temporary: records can disappear when the app is rebuilt or restarted. They can be retrieved again from PubMed. For durable institutional deployment, use persistent server storage or a managed database.

## Before calling the deployment verified

Run `python -m pip install -r requirements.txt` followed by `python -m pytest -q` in a Python environment (a GitHub Codespace is an option). Then complete the live retrieval check above. Syntax checking alone does not verify runtime or network behavior.

## Troubleshooting

- Missing module: confirm `requirements.txt` is in the repository root.
- Entrypoint missing: set the main file to `app.py` and check the upload layout.
- PubMed timeout or HTTP 429: retry later; saved records remain available.
- Institutional browser blocks the hosted URL: ask IT whether `*.streamlit.app` is allowed. The Python server, dependency downloads, and PubMed API calls run in the cloud.

Official instructions: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
