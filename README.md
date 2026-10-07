# Delta's competitive position in New York

**Independent analytics case study by Brandon Bardales · May 2026**

[![Open dashboard](https://img.shields.io/badge/Open_dashboard-Streamlit-C8102E?style=for-the-badge)](https://delta-nyc-dashboard.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.13-003366?style=flat-square)
![SQL](https://img.shields.io/badge/Offline_SQL-DuckDB-287D8E?style=flat-square)
![Data](https://img.shields.io/badge/Data-BTS_T--100-596979?style=flat-square)

## Business question

**What is Delta's competitive position in New York in May 2026?**

Compare passenger share, seat supply, occupancy, and flights across airlines,
airports, routes, and months. These measures inform capacity and revenue-management
discussions; they do not establish pricing power or profitability.

## May 2026 snapshot

Delta ranks **second by passenger share** in both views.

| Delta measure | NYC core: JFK + LGA + EWR | Wider BTS City Market 31703 |
|---|---:|---:|
| Passenger share | **21.81%** | **21.07%** |
| Seat supply share | **21.12%** | **20.31%** |
| Distance-weighted occupancy | **84.3%** | **84.3%** |
| Flights operated | **5,694** | **5,746** |

> [!NOTE]
> The dashboard opens on **NYC core**. Choose **NYC (City Market ID 31703)**
> for the wider metropolitan view used in the executive summary.

## Technologies and platforms

| Tool | Use in this project |
|---|---|
| **Python + pandas** | Data preparation, table joins, filtering, and presentation calculations. |
| **DuckDB + SQL** | Analytical database and SQL queries for preparing the data offline. |
| **Streamlit + Altair** | Interactive dashboard, charts, filters, tables, and CSV downloads. |
| **GitHub** | Hosts the published website code and prepared datasets. |
| **Streamlit Community Cloud** | Hosts the [live dashboard](https://delta-nyc-dashboard.streamlit.app). |

## Source databases and coverage

Data comes from the **U.S. Bureau of Transportation Statistics (BTS), through
its TranStats website**:

- [T-100 Domestic Market — All Carriers](https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=GED&QO_fu146_anzr=Nv4+Pn44vr45): on-flight passenger traffic and passenger share.
- [T-100 Domestic Segment — All Carriers](https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=GEE&QO_fu146_anzr=Nv4+Pn44vr45): nonstop flight legs, seats, departures, and distance-weighted occupancy.
- [BTS City Market ID definition and lookup][city-market]: explains how airports are grouped into the same city market.

**Coverage:** full-year 2024 and 2025; January–June 2026.

**Market selection:** NYC core includes departures from **JFK, LGA, and EWR**.
The wider NYC view selects records where **Origin City Market ID = 31703**,
using the BTS grouping. Airport names come from the BTS Airport ID lookup.

Both views include domestic departures in **scheduled passenger/cargo service
(Class F)**. Regional operators remain separate, and shares compare each airline
with all airlines in the selected market. Occupancy is passenger-miles divided
by available seat-miles; missing coverage remains blank.

## How the files feed the website

**BTS source ZIPs → local Python/DuckDB SQL pipeline → validated CSVs → Streamlit**

| Repository file | Purpose |
|---|---|
| [`app.py`](app.py) | Website entrypoint, layout, controls, charts, and downloads. |
| [`dashboard_model.py`](dashboard_model.py) | Loads prepared tables and supplies comparisons, routes, and history. |
| [`data_v2/`](data_v2/) | Prepared passenger, capacity, route, airport, airline, and coverage tables, plus a source [manifest](data_v2/build_manifest.json). |
| [`requirements.txt`](requirements.txt) | Pinned Python dependencies. |
| [`.streamlit/config.toml`](.streamlit/config.toml) and [`assets/`](assets/) | Theme, logo, and [attribution](assets/SOURCES.md). |

The website loads saved CSVs for fast filtering. This repository contains the
**app and prepared data**; the DuckDB/SQL preparation pipeline is maintained
separately in the local development project.

## Explore the dashboard

Use the sidebar to compare airlines and airports, **Routes** to inspect airport
pairs, and **History & seasonality** to compare the same month across years.

---

Independent work by **Brandon Bardales**; not an official Delta Air Lines publication.

[city-market]: https://www.transtats.bts.gov/FieldInfo.asp?Svryq_Qr5p=b4vtv0%FDNv42146%FP%FDPv6B%FDZn4xr6%FDVQ.%FDPv6B%FDZn4xr6%FDVQ%FDv5%FDn0%FDvqr06vsvpn6v10%FD07zor4%FDn55vt0rq%FDoB%FDhf%FDQbg%FD61%FDvqr06vsB%FDn%FDpv6B%FDzn4xr6.%FD%FDh5r%FD6uv5%FDsvryq%FD61%FDp1051yvqn6r%FDnv421465%FD5r48v0t%FD6ur%FD5nzr%FDpv6B%FDzn4xr6.&Svryq_gB2r=a7z&Y11x72_gnoyr=Y_PVgl_ZNeXRg_VQ&gnoyr_VQ=GED&flf_gnoyr_anzr=g_gEDDQ_ZNeXRg_NYY_PNeeVRe&fB5_Svryq_anzr=beVTVa_PVgl_ZNeXRg_VQ
