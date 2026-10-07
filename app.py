"""Dashboard V2: run with python -m streamlit run app.py."""
from pathlib import Path
from html import escape
import base64,calendar,math
import streamlit as st
import pandas as pd
import altair as alt
from dashboard_model import load_data,period,available,comparison,route_table,history_grid,CORE
ROOT=Path(__file__).resolve().parent
NAVY='#003366';RED='#C8102E';GRAY='#AAB9C7'
st.set_page_config(page_title='New York | Airline competitive position',page_icon='✈',layout='wide')
st.markdown('''<style>
.block-container {padding-top:4rem;max-width:1600px;padding-bottom:3rem}
h1,h2,h3 {color:#003366;letter-spacing:-.025em}
[data-testid="stSidebar"] {background:#F2F5F8}
[data-testid="stMetricValue"] {color:#003366}
.eyebrow {color:#526879;font-size:.8rem;letter-spacing:.12em;font-weight:650}
.kpi-note {font-size:.86rem;line-height:1.45;color:#43596b;min-height:4.1rem}
.chart-row {display:grid;grid-template-columns:minmax(180px,280px) minmax(120px,1fr) 72px;gap:8px;align-items:center;min-height:26px;margin:0;padding:2px 0;border-bottom:1px solid #edf1f5;font-size:14px}
.airline-label {color:#223b50;line-height:1.35;overflow-wrap:anywhere;display:flex;align-items:center;gap:6px;flex-wrap:wrap;justify-content:flex-end;text-align:right}
.airline-label img {width:63px;height:auto}
.bar-track {height:17px;background:#F1F4F7;border-radius:3px}
.bar-fill {height:17px;border-radius:3px}
.bar-value {font-variant-numeric:tabular-nums;color:#003366;text-align:right;font-weight:600}
.chart-axis {display:grid;grid-template-columns:minmax(180px,280px) minmax(120px,1fr) 72px;gap:8px;color:#586d7c;font-size:12px}
.chart-axis div {display:flex;justify-content:space-between}
.legend {color:#526879;font-size:13px;margin:6px 0}
@media(max-width:850px) {.chart-row,.chart-axis {grid-template-columns:minmax(135px,1.3fr) minmax(75px,1.4fr) 62px;font-size:12px;gap:7px}.block-container {padding-left:1rem;padding-right:1rem}}
</style>''',unsafe_allow_html=True)
@st.cache_data
def tables():return load_data(ROOT)
try:data=tables()
except (OSError,ValueError):
    st.error('The prepared V2 data is missing or incomplete. Copy the data_v2 folder beside app.py, then restart.');st.stop()
airports=data['airports'];airport_names=dict(zip(airports.airport,airports.display_name))
scopes={'NYC core: Kennedy, LaGuardia & Newark':'NYC_CORE'}
scopes.update({airport_names[a]:a for a in CORE});scopes['NYC (City Market ID 31703)']='CITY_31703'
logo=ROOT/'assets/delta_logo.png'
logo_url='data:image/png;base64,'+base64.b64encode(logo.read_bytes()).decode() if logo.exists() else ''
st.sidebar.title('Explore the data')
scope_label=st.sidebar.selectbox('Airport market',list(scopes),key='scope');scope=scopes[scope_label]
years=sorted(data['coverage'].YEAR.unique(),reverse=True);year=st.sidebar.selectbox('Year',years,key='year')
months=sorted(data['coverage'].loc[data['coverage'].YEAR==year,'MONTH'].unique())
month=st.sidebar.selectbox('Month',months,index=months.index(5) if 5 in months else 0,format_func=lambda m:calendar.month_name[int(m)],key='month')
current=comparison(data,year,month,scope)
labels=dict(zip(current.AIRLINE_ID.astype(int),current.UNIQUE_CARRIER_NAME));ids=sorted(labels,key=lambda x:labels[x])
carrier=st.sidebar.selectbox('Airline operating the flights',ids,index=ids.index(19790) if 19790 in ids else 0,format_func=lambda x:labels[x],key='carrier')
selected=current[current.AIRLINE_ID==carrier].iloc[0];name=str(selected.UNIQUE_CARRIER_NAME)
has_segment=available(data,'segment',year,month)
st.sidebar.caption('Each share compares this airline with all airlines in the selected airport market and month.')
st.sidebar.divider()
st.sidebar.caption('Independent analysis by Brandon Bardales.')
st.sidebar.markdown('**Source: Bureau of Transportation Statistics**')
st.sidebar.markdown('<a href="https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=GED&amp;QO_fu146_anzr=Nv4+Pn44vr45" target="_blank" rel="noopener noreferrer">Air Carriers: T-100 Domestic Market (All Carriers)</a><br><br><a href="https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=GEE&amp;QO_fu146_anzr=Nv4+Pn44vr45" target="_blank" rel="noopener noreferrer">Air Carriers: T-100 Domestic Segment (All Carriers)</a>',unsafe_allow_html=True)
st.title(f'How does {name} compete in New York?')
st.markdown(f'**{calendar.month_name[month]} {year} | {scope_label}**')
if scope=='NYC_CORE':st.caption(' · '.join(airport_names[a] for a in CORE))
st.caption('Market Scope: Domestic U.S. traffic departing the selected airports. International traffic is excluded.')
st.caption('Service Scope: Scheduled passenger/cargo service (Class F). Excluded: other service classes, as scheduled all-cargo (Class G) and non-scheduled civilian passenger/cargo (Class L).')
st.caption('Airlines are counted by the company operating/reporting the flights. Regional operators such as Endeavor and Republic remain separate; their passengers are not automatically added to Delta.')
if not has_segment:st.info(f'{year} passenger history is available. Seats, seat occupancy and operated flights need the matching {year} Segment dataset; unavailable values are not zero.')
def pct(x,digits=2):return 'Not available' if pd.isna(x) else f'{x:.{digits}%}'
def integer(x):return 'Not available' if pd.isna(x) else f'{x:,.0f}'
cards=[('Share of passengers carried',pct(selected.market_passenger_share),'Market passenger share: this airline’s recorded passenger traffic divided by all airlines’ passenger traffic in this market.'),
       ('Share of seats supplied',pct(selected.seat_share),'Seat share: this airline’s available seats divided by all airlines’ seats. This measures supply, whether seats were filled or empty.'),
       ('Seat occupancy, distance-weighted',pct(selected.load_factor,1),'Load factor: occupied seat-miles divided by available seat-miles. A seat flown twice as far contributes twice as much capacity to this calculation.'),
       ('Departure flights operated',integer(selected.departures_performed),'Actual departures operated in scheduled passenger/cargo service. One departure is one flight, not one passenger.')]
metric_sources=[
    'Source: T-100 Domestic Market. Uses PASSENGERS. Passenger traffic means recorded passenger movements, not unique people across all their trips.',
    'Source: T-100 Domestic Segment. Uses SEATS. Airline seats divided by the seats supplied by all airlines in the selected airport market and month.',
    'Source: T-100 Domestic Segment. Sum(PASSENGERS × DISTANCE) ÷ Sum(SEATS × DISTANCE). One seat flown 1,000 miles counts ten times as much as one flown 100 miles. See the worked example in How to read the metrics.',
    'Source: T-100 Domestic Segment. Sum of DEPARTURES_PERFORMED; actual operated departures, not DEPARTURES_SCHEDULED.'
]
for col,(label,value,explanation),source in zip(st.columns(4,gap='medium'),cards,metric_sources):
    with col:
        st.metric(label,value,help=source);st.markdown(f'<div class="kpi-note">{escape(explanation)}</div>',unsafe_allow_html=True)

def table_columns(frame,percentages=()):
    # Numeric values stay numeric for sorting and CSV exports; formatting is display-only.
    return {c:st.column_config.NumberColumn(format='percent' if c in percentages else '%,d',alignment='left')
            if pd.api.types.is_numeric_dtype(frame[c]) else st.column_config.TextColumn(alignment='left') for c in frame.columns}

overview,routes,history,method,future=st.tabs(['Competitive position','Routes','History & seasonality','How to read the metrics','Future improvements'])

def airline_bars(frame):
    frame=frame.sort_values('market_passengers',ascending=False,na_position='last');maxshare=frame.market_passenger_share.max();maximum=max(.05,math.ceil(float(maxshare)*20)/20)
    parts=['<div role="img" aria-label="Passenger share by operating airline">']
    for r in frame.itertuples():
        value=r.market_passenger_share;color=RED if r.AIRLINE_ID==carrier else NAVY if r.AIRLINE_ID==19790 else GRAY
        img=f'<img src="{logo_url}" alt="Delta logo">' if r.AIRLINE_ID==19790 and logo_url else ''
        width=0 if pd.isna(value) else value/maximum*100;label=escape(r.UNIQUE_CARRIER_NAME)
        parts.append(f'<div class="chart-row"><div class="airline-label">{label}{img}</div><div class="bar-track"><div class="bar-fill" style="width:{width:.5f}%;background:{color}" title="{label}: {pct(value)}"></div></div><div class="bar-value">{pct(value)}</div></div>')
    parts.append(f'<div class="chart-axis"><span></span><div><span>0%</span><span>{maximum/2:.0%}</span><span>{maximum:.0%}</span></div><span></span></div></div>')
    st.markdown(''.join(parts),unsafe_allow_html=True)
    st.markdown('<div class="legend">Selected airline highlighted in red.</div>',unsafe_allow_html=True)

with overview:
    st.subheader('Who carries the passengers?');st.caption('Every operating airline is shown, with its full name and passenger share.')
    airline_bars(current);st.divider();st.subheader(f'Where does {name} have the largest share?')
    footprint=period(data['market_scope'],year,month);footprint=footprint[(footprint.AIRLINE_ID==carrier)&footprint.scope.isin(CORE)].copy();footprint['Airport']=footprint.scope.map(airport_names)
    for airport in CORE:
        if airport not in footprint.scope.values:
            covered=not period(data['market_scope'],year,month,airport).empty
            footprint=pd.concat([footprint,pd.DataFrame([{'scope':airport,'Airport':airport_names[airport],'market_passenger_share':0 if covered else float('nan'),'market_passengers':0}])],ignore_index=True)
    xmax=max(.05,float(footprint.market_passenger_share.max())*1.20)
    base=alt.Chart(footprint).encode(y=alt.Y('Airport:N',sort='-x',axis=alt.Axis(labelLimit=450,labelFontSize=14,labelOverlap=False),title=None),x=alt.X('market_passenger_share:Q',scale=alt.Scale(domain=[0,xmax]),axis=alt.Axis(format='%',labelFontSize=13,tickCount=6),title='Share of passengers carried at each airport'))
    chart=base.mark_bar(color=NAVY,size=25).encode(tooltip=['Airport',alt.Tooltip('market_passenger_share:Q',format='.2%')])+base.mark_text(align='left',dx=7,color=NAVY,fontSize=14).encode(text=alt.Text('market_passenger_share:Q',format='.2%'))
    st.altair_chart(chart.properties(height=170).configure_view(stroke=None),width='stretch')
    st.caption('All three core airports are shown for context, regardless of the sidebar airport. Each share uses that airport’s own passenger total. All bars have the same color. This chart uses Market passengers consistently with the top KPI.')
    st.subheader('What changes with your selection')
    ordered=current[current.market_passengers.notna()].sort_values('market_passengers',ascending=False)
    if carrier in ordered.AIRLINE_ID.values:
        rank=list(ordered.AIRLINE_ID).index(carrier)+1
        st.write(f'**Competitive rank:** {name} ranks **{rank} of {len(ordered)}** reporting airlines with Market passenger records in this airport market.')
    else:st.write('**Competitive rank:** unavailable because this operator has no Market passenger record in the selected scope and month.')
    previous=period(data['market_scope'],year-1,month,scope);prior=previous[previous.AIRLINE_ID==carrier]
    if not prior.empty and pd.notna(selected.market_passenger_share):
        p=prior.iloc[0];gap=100*(selected.market_passenger_share-p.market_passenger_share);growth=selected.market_passengers/p.market_passengers-1 if p.market_passengers>0 else float('nan')
        st.write(f'**Same month last year:** passenger share changed **{gap:+.2f} percentage points** versus {calendar.month_name[month]} {year-1}'+(f'; passengers carried (recorded passenger movements) changed **{growth:+.1%}**.' if pd.notna(growth) else '.'))
    if footprint.market_passengers.sum()>0:
        top=footprint.sort_values('market_passengers',ascending=False).iloc[0];concentration=top.market_passengers/footprint.market_passengers.sum()
        st.write(f'**Airport concentration:** {top.Airport} accounts for **{concentration:.1%}** of this airline’s passengers carried across the three core airports. This is the airline’s own mix, not its share of the airport.')
    with st.expander('Compare all airlines in a table',expanded=True):
        display=current[['UNIQUE_CARRIER_NAME','market_passengers','market_passenger_share','seats','seat_share','load_factor','departures_performed']].rename(columns={'UNIQUE_CARRIER_NAME':'Airline','market_passengers':'Passengers carried','market_passenger_share':'Passenger share','seats':'Seats supplied','seat_share':'Seat supply share','load_factor':'Distance-weighted occupancy','departures_performed':'Flights operated'})
        st.dataframe(display,hide_index=True,width='stretch',column_config=table_columns(display,['Passenger share','Seat supply share','Distance-weighted occupancy']))
        st.download_button('Download airline comparison',display.to_csv(index=False),f'airline_comparison_{scope}_{year}_{month:02}.csv','text/csv')

with routes:
    st.subheader('Which airport pairs matter?');st.write('A route is a **directional airport pair**: departing airport → arriving airport. New York to Atlanta is separate from Atlanta to New York.')
    choices=['Passengers carried (Market)','Seats and nonstop flights (Segment)'];view=st.radio('View',choices,index=1 if has_segment else 0,horizontal=True,key='route_view')
    r=route_table(data,year,month,scope,carrier)
    st.caption('Nonstop means one flight leg with no intermediate landing. A journey with a stop has multiple legs. Flight capacity means the seats and flights supplied; passenger traffic means the passenger movements actually recorded.')
    if view==choices[1] and not has_segment:st.info(f'Flight-capacity data has not been supplied for {year}. Select the passenger view to explore available routes.')
    else:
        search=st.text_input('Find an airport or city',placeholder='e.g. Atlanta, Los Angeles, JFK',key='route_search')
        if search:
            matching=pd.Series(False,index=r.index)
            for col in ['Origin airport','Destination airport','Origin city','Destination city']:
                matching=matching|r[col].str.contains(search,case=False,regex=False,na=False)
            r=r[matching]
        if view==choices[0]:
            r=r[r.market_passengers.notna()];show=r[['Origin airport','Destination airport','market_passengers','Source records']].rename(columns={'market_passengers':'Passengers carried'}).sort_values('Passengers carried',ascending=False)
            st.caption('On-flight passenger markets can include an intermediate stop. This is not a complete ticket itinerary and should not be labeled nonstop demand.')
        else:
            minimum=st.slider('Minimum flights operated',0,100,0,key='min_departures');r=r[r.departures_performed.notna()&(r.departures_performed>=minimum)]
            show=r[['Origin airport','Destination airport','segment_passengers','seats','departures_performed','load_factor','route_seat_share','Source records']].rename(columns={'segment_passengers':'Passengers on nonstop legs','seats':'Seats supplied','departures_performed':'Flights operated','load_factor':'Seat occupancy','route_seat_share':'Route seat supply share'}).sort_values('Seats supplied',ascending=False)
        st.dataframe(show,hide_index=True,width='stretch',column_config=table_columns(show,['Seat occupancy','Route seat supply share']))
        st.caption(f'{len(show):,} airport pairs shown. Blank values mean unavailable; they do not imply zero activity. Same-airport records with zero reported distance have undefined distance-weighted occupancy. Reported source values are retained, including rare passenger counts above seats.')
        st.download_button('Download these routes',show.to_csv(index=False),f'routes_{carrier}_{scope}_{year}_{month:02}.csv','text/csv')
    st.markdown('''**Read the route columns**

| Column | Meaning |
|---|---|
| Passengers carried | Count of recorded passenger movements between the airports in the Market source. This is what passenger traffic means; it is not a count of unique individuals across all trips. |
| Passengers on nonstop legs | People transported on the physical nonstop flight leg, including connecting travelers. |
| Seats supplied | Available passenger seats on those flights, filled or empty. |
| Flights operated | Actual departures flown; not the planned schedule or passenger count. |
| Seat occupancy | Passenger-miles divided by seat-miles. On one airport pair with constant distance, this equals passengers divided by seats. |
| Route seat supply share | This airline’s seats divided by every airline’s seats on the same directional pair and month. |
| Source records | Market + Segment: both sources contain this airline/pair/month. Market only: passenger-movement records only. Segment only: aircraft-leg records with seats and flights only. These labels describe source availability, not performance. |
''')

with history:
    st.subheader('Separate seasonal patterns from year-over-year change')
    metrics={'Passenger share':'market_passenger_share','Seat supply share':'seat_share','Distance-weighted seat occupancy':'load_factor','Departure flights operated':'departures_performed'}
    metric_label=st.selectbox('Historical metric',list(metrics),key='history_metric');grid=history_grid(data,carrier,scope,metrics[metric_label]);sortyears=sorted(grid.Year.unique());is_count=metrics[metric_label]=='departures_performed'
    colors=['#99B0C7','#3974A5',RED] if len(sortyears)==3 else [NAVY,RED,'#3974A5','#99B0C7','#607788'][:len(sortyears)]
    chart=alt.Chart(grid).mark_line(point=alt.OverlayMarkDef(size=75),strokeWidth=3).encode(
        x=alt.X('Month:Q',scale=alt.Scale(domain=[1,12]),axis=alt.Axis(values=list(range(1,13)),labelExpr="['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][datum.value-1]",labelAngle=0,labelFontSize=14),title=None),
        y=alt.Y('Value:Q',axis=alt.Axis(format=',.0f' if is_count else '%',labelFontSize=14),title=metric_label,scale=alt.Scale(zero=True)),
        color=alt.Color('Year:N',scale=alt.Scale(domain=sortyears,range=colors),legend=alt.Legend(orient='top',labelFontSize=14,title=None)),
        tooltip=['Year',alt.Tooltip('Month:Q',title='Month'),alt.Tooltip('Value:Q',format=',.0f' if is_count else '.2%',title=metric_label),'Coverage'])
    st.altair_chart(chart.properties(height=380).configure_view(stroke=None),width='stretch')
    st.caption('All 12 months remain on the axis. Missing data leaves a gap; it is never filled with zero or carried forward. Compare the same month across years to reduce seasonal distortion. ')
    st.subheader(f'{calendar.month_name[month]} across years');same=grid[grid.Month==month][['Year','Value','Coverage']].rename(columns={'Value':metric_label})
    st.dataframe(same,hide_index=True,width='stretch',column_config=table_columns(same,[] if is_count else [metric_label]))

with method:
    st.subheader('Four measures, four different questions')
    st.markdown('''| Measure | Question answered | Simple example |
|---|---|---|
| Passenger share (Market) | How much recorded passenger traffic did this airline carry? | 20 of 100 passenger movements → 20% share. |
| Seat supply share (Segment) | How much available seat supply did it operate? | 30 of 100 seats → 30% share, filled or empty. |
| Distance-weighted seat occupancy | How much available seat-distance was used? | 80 occupied seat-miles for every 100 available → 80% load factor. |
| Departure flights operated | How many physical flights departed? | One plane departing counts once, whether it carries 50 or 150 passengers. |

**Traffic and supply are different.** Passenger traffic is realized travel that occurred, not all demand that could have existed. Seats measure capacity supplied. Neither tells us the fare paid or profit earned.

**Why distance changes load factor.** A seat flown 1,000 miles supplies ten times as many seat-miles as one flown 100 miles. Network load factor gives longer flights more weight. It is not the simple average of flight percentages.

**Worked example: two flights with different distances.**

| Flight | Seats | Passengers | Distance | Available seat-miles | Occupied passenger-miles |
|---|---:|---:|---:|---:|---:|
| Short flight | 100 | 90 | 100 miles | 10,000 | 9,000 |
| Long flight | 100 | 50 | 1,000 miles | 100,000 | 50,000 |
| Total | 200 | 140 | — | 110,000 | 59,000 |

Simply counting seats gives 140 ÷ 200 = **70%**. Distance-weighted occupancy is
59,000 ÷ 110,000 = **53.6%**. The longer flight was less full and supplied ten times
the seat-distance, so it has more influence. We multiply each record's passengers
and seats by its distance, sum each side, then divide. We do not average the two
flight percentages. On a single route with a constant positive distance, distance
cancels out and the result equals passengers divided by seats.

**Market versus Segment.** Market records on-flight passenger movement between origin and destination. Segment records physical nonstop legs. A passenger traveling A → B → C on the same flight can produce one A → C Market movement and two Segment movements. Full connecting tickets and unique travelers cannot be reconstructed from these totals.

**Compare like with like.** Use Segment passenger share versus Segment seat share for capacity-utilization comparisons. Use Market passenger share as the main traffic-position measure.

**Geography.** NYC core is John F. Kennedy International, LaGuardia and Newark Liberty International. Wider metro uses BTS City Market 31703, including peripheral airports. Full names come from the BTS Airport ID reference; IDs drive the joins. Current reference labels may differ from historical airport names.

**Service and carrier identity.** Class F is scheduled passenger/cargo service. All-cargo-only and charter classes are excluded. A ticket may say Delta while a regional company operates the flight. These records identify the operating/reporting company, so regional operators remain separate. Republic can serve multiple brands; adding all its passengers to Delta would overstate Delta. These are operator shares, not complete Delta-brand shares. Class G is scheduled all-cargo; L is non-scheduled civilian passenger/cargo. Class Z means all services, not charter.

**Scope.** Domestic origin traffic does not measure the full international NYC market, unique local residents, fares, profitability or unserved demand.

**How the app works.** Python and DuckDB prepare small monthly tables before presentation. The app reads and caches them in memory. Filters do not modify the ZIPs, rerun the pipeline, or require a database server.
''')
with future:
    st.subheader('Useful next extensions')
    st.markdown('''1. **Extend recent history:** add 2023 Market and Segment if another seasonal comparison would strengthen the story. Capacity history for all months of 2024 and 2025 is included.
2. **Five-year context if useful:** add 2022–2023 Market and Segment after the three-year story is understood. Track source coverage by year/month.
3. **Automated refreshes:** a documented BTS download/API workflow where supported, with source-date checks and validation before published updates.
4. **Commercial-brand and pricing context:** a suitable ticket/schedule source, potentially DB1C, could support fares and marketing-carrier analysis. This dashboard makes no such estimates.
5. **Booking and operating context:** authorized booking curves, fares, schedule timing and costs could support specific revenue-management decisions.
''')
st.caption('Source: U.S. Bureau of Transportation Statistics, T-100 Domestic Market / Segment and Airport ID reference. Independent analytical case study.')
