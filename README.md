# New York airline competitive position

Streamlit dashboard of U.S. domestic departing traffic using BTS T-100 Market
and Segment data. The default view is Delta, NYC core, May 2026.

The app reads the saved tables in `data_v2/`; no pipeline rebuild, database,
source ZIPs, secrets, or external data download is needed at startup.
Existing coverage is 2024-2025 and January-June 2026. Regional operators remain
separate. Seat occupancy is distance-weighted; missing coverage is not zero.

## Deployment

Read [UPLOAD_GUIDE.txt](UPLOAD_GUIDE.txt) for plain-language instructions.
Upload this folder's contents to the repository root, keeping subfolders intact.
Use `app.py` as the entrypoint and Python **3.13** in Streamlit Community Cloud.
Dependencies are declared in `requirements.txt`; secrets can be left empty.

The original source ZIP archive and offline pipeline remain in the local
project. This repository copy contains the website and its prepared data.
Logo attribution is in [assets/SOURCES.md](assets/SOURCES.md).
