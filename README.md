# Delta's competitive position in New York

**Independent analytics case study by Brandon Bardales · May 2026**

[![Open dashboard](https://img.shields.io/badge/Open_dashboard-Streamlit-C8102E?style=for-the-badge)](https://delta-nyc-dashboard.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.13-003366?style=flat-square)
![SQL](https://img.shields.io/badge/Offline_SQL-DuckDB-287D8E?style=flat-square)
![Data](https://img.shields.io/badge/Data-BTS_T--100-596979?style=flat-square)

## Business question

**What is Delta's competitive position in New York in May 2026, and where do
passenger share, capacity, and seat occupancy suggest further commercial investigation?**

The dashboard compares airlines, airports, routes, and monthly history to support
capacity and revenue-management discussions. Market share and occupancy provide
context; they do not establish pricing power or profitability.

## May 2026 snapshot

Delta ranks **second by passenger share** in both views.

| Delta measure | NYC core: JFK + LGA + EWR | Wider BTS City Market 31703 |
|---|---:|---:|
| Passenger share | **21.81%** | **21.07%** |
| Seat supply share | **21.12%** | **20.31%** |
| Distance-weighted occupancy | **84.3%** | **84.3%** |
| Flights operated | **5,694** | **5,746** |

> [!NOTE]
> The dashboard defaults to **NYC core**. The executive summary uses **City Market
> 31703**. Select that wider market in the dashboard to compare the same scope.

## Technologies and platforms

| Tool | Use in this project |
|---|---|
| **Python + pandas** | Data preparation, table joins, filtering, and presentation calculations. |
| **DuckDB + SQL** | Local analytical database and offline aggregation/validation pipeline. |
| **Streamlit + Altair** | Interactive dashboard, charts, filters, tables, and CSV downloads. |
| **GitHub** | Hosts the published website code and prepared datasets. |
| **Streamlit Community Cloud** | Hosts the [live dashboard](https://delta-nyc-dashboard.streamlit.app). |

## Source databases and coverage

Data comes from the **U.S. Bureau of Transportation Statistics (BTS), through
its TranStats website**:

- [T-100 Domestic Market — All Carriers](https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=GED&QO_fu146_anzr=Nv4+Pn44vr45): on-flight passenger traffic and passenger share.
- [T-100 Domestic Segment — All Carriers](https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=GEE&QO_fu146_anzr=Nv4+Pn44vr45): nonstop flight legs, seats, departures, and distance-weighted occupancy.
- [BTS Airport ID lookup](https://www.transtats.bts.gov/Download_Lookup.asp?Y11x72=Y_NVecbeg_VQ): airport identifiers and display names.

Coverage: **January–December 2024 and 2025; January–June 2026**. Analysis includes
domestic departures in scheduled passenger/cargo service (Class F). Regional
operators remain separate; missing coverage is not filled with zero. Occupancy
is total passenger-miles divided by total available seat-miles.

## How the files feed the website

**BTS source ZIPs → local Python/DuckDB SQL pipeline → validated CSVs → Streamlit**

| Repository file | Purpose |
|---|---|
| [`app.py`](app.py) | Website entrypoint, layout, controls, charts, and downloads. |
| [`dashboard_model.py`](dashboard_model.py) | Loads prepared tables and supplies comparisons, routes, and history. |
| [`data_v2/`](data_v2/) | Seven saved CSV tables and the [build manifest](data_v2/build_manifest.json) documenting lineage and checks. |
| [`requirements.txt`](requirements.txt) | Pinned Python dependencies. |
| [`.streamlit/config.toml`](.streamlit/config.toml) and [`assets/`](assets/) | Theme, logo, and [attribution](assets/SOURCES.md). |

This repository contains the **website and prepared data**. The raw ZIP archive,
DuckDB database, SQL preparation scripts, and full test suite remain in the local
development project. The hosted app reads saved CSVs; it does not query a live
database or rebuild the pipeline when a visitor changes a filter.

## Explore and verify

1. **Compare:** switch airlines and airports in the sidebar.
2. **Investigate:** open **Routes** and search an airport or city.
3. **Contextualize:** open **History & seasonality** to compare the same month across years.

Before deployment, the local project passed **8 pipeline tests, 32 dashboard
checks, and all 6 source-ZIP fingerprint checks**. The author also tested the
hosted app in Incognito and on another device. These are completed checks,
not automated GitHub CI results.

<details>
<summary>Run locally with Python 3.13</summary>

From the repository folder, preferably in a virtual environment:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

No credentials, database server, or source-data download is required.

</details>

---

Independent work by **Brandon Bardales**; not an official Delta Air Lines publication.
