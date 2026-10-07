"""Read-only presentation model. Source ingestion never occurs on an app rerun."""
from pathlib import Path
import json
import pandas as pd
CORE=['JFK','LGA','EWR']

def load_data(root):
    folder=Path(root)/'data_v2'
    manifest=json.loads((folder/'build_manifest.json').read_text(encoding='utf-8'))
    if manifest['status']!='PASS':raise ValueError('Prepared dataset did not pass validation.')
    return {n:pd.read_csv(folder/(n+'.csv')) for n in ['market_scope','segment_scope','market_route','segment_route','carriers','airports','coverage']}

def period(df,year,month,scope=None):
    out=df[(df.YEAR==year)&(df.MONTH==month)]
    return (out[out.scope==scope] if scope is not None else out).copy()

def available(data,kind,year,month):
    c=data['coverage'];return bool(((c.kind==kind)&(c.YEAR==year)&(c.MONTH==month)).any())

def comparison(data,year,month,scope):
    m=period(data['market_scope'],year,month,scope);s=period(data['segment_scope'],year,month,scope)
    df=m.merge(s,on=['YEAR','MONTH','AIRLINE_ID','scope'],how='outer',validate='one_to_one')
    return df.merge(period(data['carriers'],year,month),on=['YEAR','MONTH','AIRLINE_ID'],validate='many_to_one')

def route_table(data,year,month,scope,carrier):
    a=data['airports'];names=a.set_index('airport_id').display_name
    if scope=='NYC_CORE':ids=a.loc[a.airport.isin(CORE),'airport_id']
    elif scope=='CITY_31703':ids=a.loc[a.city_market_id==31703,'airport_id']
    else:ids=a.loc[a.airport==scope,'airport_id']
    m=period(data['market_route'],year,month);s=period(data['segment_route'],year,month)
    m=m[m.ORIGIN_AIRPORT_ID.isin(ids)];s=s[s.ORIGIN_AIRPORT_ID.isin(ids)]
    totals=s.groupby(['ORIGIN_AIRPORT_ID','DEST_AIRPORT_ID']).seats.sum(min_count=1).rename('all_route_seats')
    s=s.join(totals,on=['ORIGIN_AIRPORT_ID','DEST_AIRPORT_ID'])
    s['route_seat_share']=s.seats/s.all_route_seats.replace(0,float('nan'))
    df=m.merge(s,on=['YEAR','MONTH','AIRLINE_ID','ORIGIN_AIRPORT_ID','DEST_AIRPORT_ID'],how='outer',validate='one_to_one',indicator=True)
    df=df[df.AIRLINE_ID==carrier].copy()
    df['Origin airport']=df.ORIGIN_AIRPORT_ID.map(names);df['Destination airport']=df.DEST_AIRPORT_ID.map(names)
    cities=a.set_index('airport_id').city_name
    df['Origin city']=df.ORIGIN_AIRPORT_ID.map(cities);df['Destination city']=df.DEST_AIRPORT_ID.map(cities)
    df['Source records']=df['_merge'].map({'both':'Market + Segment','left_only':'Market only','right_only':'Segment only'}).astype(str)
    return df

def history_grid(data,carrier,scope,metric):
    kind='market' if metric=='market_passenger_share' else 'segment';source=data[kind+'_scope'];rows=[]
    for year in sorted(data['coverage'].YEAR.unique()):
        for month in range(1,13):
            covered=available(data,kind,year,month);selected=period(source,year,month,scope);r=selected[selected.AIRLINE_ID==carrier];v=float('nan')
            if covered and not selected.empty:
                if not r.empty:v=r.iloc[0][metric]
                elif metric!='load_factor':v=0.0
            rows.append({'Year':str(year),'Month':month,'Value':v,'Coverage':'Available' if covered else 'Not supplied'})
    return pd.DataFrame(rows)
