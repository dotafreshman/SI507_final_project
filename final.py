import json, requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from secret import *
# from datetime import datetime
# import numpy as np

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Palau': 'PW',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}
month={
    "January":1,"February":2,"March":3,"April":4,"May":5,"June":6,
    "July":7,"August":8,"September":9,"October":10,"November":11,"December":12
}

def make_request_using_cache(url,header):
    unique_ident = url

    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        #print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        #print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(url,headers=header)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

def web_scrape():
    base_url="https://www.gunviolencearchive.org"
    para="/reports/mass-shootings/2014"
    #para="/mass-shooting"
    #header={'User-Agent': 'SI_CLASS'}
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/51.0.2704.63 Safari/537.36'}
    final_list=[]
    coor_list=[]
    coor_reg=[]   #judge whether the city's already in coor_list

    for i in range(0,11):
        new_para=para
        if i>0:
            new_para=para+"?page="+str(i)
        html=make_request_using_cache(base_url+new_para,header)
        soup=BeautifulSoup(html,'html.parser')

        tables=soup.find('table')

        for tr in tables.findAll('tr')[1:]:
            row={}
            td=tr.findAll('td')
            #print(td[0])
            row['id']=td[0].text;


            #print(int(td[1].text.split(' ')[2])*10000,int(td[1].text.split(" ")[1][:-1])*100,month[td[1].text.split(' ')[0]])
            row['date']=td[1].text;
            row['state']=us_state_abbrev[td[2].text];row['city']=td[3].text;
            row['address']=td[4].text;row['kill']=td[5].text;row['injure']=td[6].text
            final_list.append(row)
            #print(row)
            #print(base_url+td[7].a['href'])


            #search lat and lng for address
            if td[3].text not in coor_reg:
                map_url='https://maps.googleapis.com/maps/api/place/findplacefromtext/json?'
                map_para = "key=" + google_places_key + "&input=" + td[2].text+" "+td[3].text + "&inputtype=textquery" + "&fields=geometry"
                map_html = make_request_using_cache(map_url + map_para, header)
                lat = json.loads(map_html)["candidates"][0]["geometry"]["location"]["lat"]
                lng = json.loads(map_html)["candidates"][0]["geometry"]["location"]["lng"]

                row={};row['city']=td[3].text;row['lat']=lat
                row['lng']=lng;coor_list.append(row)
                coor_reg.append(td[3].text)

    # for i in final_list:print(i)
    # print(len(final_list))
    # for i in coor_list:print(i)
    # print(len(coor_list))
    return final_list,coor_list


def make_table(final_list,coor_list):
    # write into table
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    c.execute('drop table if exists city')
    c.execute('''create table city(
        id integer primary key autoincrement,
        city text,
        lat real,
        lng real
    )''')
    for i in coor_list:
        insertion=(None,i['city'],i['lat'],i['lng'])
        c.execute('INSERT INTO city VALUES (?,?,?,?)',insertion)

    c.execute('drop table if exists crime')
    c.execute('''create table crime(
            id integer,
            date text,
            kill integer,
            injure integer
        )''')
    for i in final_list:
        insertion=(i['id'],i['date'],i['kill'],i['injure'])
        c.execute("insert into crime values (?,?,?,?)",insertion)
    c.execute('drop table if exists address')
    c.execute('''create table address(
        id integer,
        state text,
        cityid integer,
        address text,
        foreign key (cityid) references city(id)
    )''')
    for i in final_list:
        insertion=(i['id'],i['state'],i['city'],i['address'])
        c.execute('insert into address values (?,?,(select id from city where city==?),?)',insertion)
    conn.commit()
    conn.close()

def plot1_map(abb,test):
    #abb="Fl"
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    lat="(select lat from city where id=address.cityid),";
    lng="(select lng from city where id=address.cityid),"
    city="(select city from city where id=address.cityid)"
    c.execute('select address,'+lat+lng+city+' from address where state=="'+abb+'"')
    lat_list=[];lng_list=[];address_list=[];city_list=[]
    for i in c.fetchall():
        lat_list.append(float(i[1]))
        lng_list.append(float(i[2]))
        address_list.append(i[0])
        city_list.append(i[3])
    #print(lat_list)
    if len(lat_list)>0:
        fig = go.Figure(go.Scattermapbox(
            lat=lat_list,
            lon=lng_list,
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=9,
                symbol='circle'
            ),
            text=address_list#city_list,
        ))


        fig.update_layout(
            autosize=True,
            hovermode='closest',
            mapbox=go.layout.Mapbox(
                accesstoken=mapbox_access_token,
                bearing=0,
                center=go.layout.mapbox.Center(
                    lat=lat_list[0],  # lat_list[0],
                    lon=lng_list[0]  # lng_list[0]
                ),
                pitch=0,
                zoom=5
            ),
        )
        if test==False:
            fig.show()
    else: print("no such state or no data")
    return lat_list,lng_list

def plot2_box(state_list,test):
    #state_list=['CA','NY','TX','PA','FL']
    qm="?"*len(state_list)
    conn=sqlite3.connect(DBNAME)
    c=conn.cursor()
    temp='(select state from address where id=crime.id)'
    c.execute('select '+temp+' as state,(injure) as victim from crime where '+temp+' in ({})'.format(','.join(qm)),state_list)
    df=pd.DataFrame(c.fetchall(),columns=['state','victims'])
    #print(df)
    fig = px.box(df,x='state',y="victims")
    if test==False:
        fig.show()
    conn.close()
    return list(df['state'])

def plot3_line(m,test):
    #m="September"

    conn=sqlite3.connect(DBNAME)
    c=conn.cursor()
    c.execute("select date,sum(kill),sum(injure) from crime group by date having date like '"+m+"%' order by date asc limit 200")

    df=pd.DataFrame(c.fetchall(),columns=['date','death','injury'])

    df['date']=pd.to_datetime(df['date'])
    df.sort_values('date',inplace=True)
    data=go.Scatter(x=list(df['date']),y=list(df['death']),name="death")
    data2=go.Scatter(x=list(df['date']),y=list(df['injury']),name="injury")


    fig=go.Figure(data=data)
    fig.add_trace(data2)
    fig.update_layout(title=m)
    if test==False:
        fig.show()
    #print(df)
    #print(list(df['date']))
    conn.close()
    return list(df['date'])

def plot4_bar(limit,test):
    #limit="10"
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    c.execute(
        "select state,count(id) from address group by state order by count(id) desc limit "+limit)
    df = pd.DataFrame(c.fetchall(), columns=['state', 'cases number'])
    fig=px.bar(df,x='state',y="cases number")
    if test==False:
        fig.show()
    conn.close()
    return list(df['state'])


def process_command(response):
    response_s=response.split(' ')
    if response_s[0]=='map':plot1_map(response_s[1],False)
    elif response_s[0]=='box':plot2_box(response_s[1:],False)
    elif response_s[0]=='line':plot3_line(response_s[1],False)
    elif response_s[0]=='bar':plot4_bar(response_s[1],False)
    else: return "no such command"
    return "command processing"

CACHE_FNAME = 'cache.json'
DBNAME='final.db'




try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

# if there was no file, no worries. There will be soon!
except:
    CACHE_DICTION = {}


if __name__=="__main__":
    final_list,coor_list=web_scrape()
    make_table(final_list,coor_list)
    #plot2_box()
    #plot1_map("MI")
    #plot4_bar()
    #for i in coor_list:print(i['city'],i['lat'],i['lng'])
    #plot3_line()
    response=""
    while response!='exit':
        response=input('Enter a command (or help): ')
        if response=="help":
            print('''
            available commands:
            map <alpha-2 state>
                ex: map TX
            line <month>
                ex: line September
            box <list of state>
                ex: box CA NY WA
            bar <limit>
                ex: bar 13
            ''')
        elif response!='exit':
            result=process_command(response)
            print(result)
    print("bye")
# base_url="https://www.gunviolencearchive.org"
# para="/reports/mass-shootings/2014"
# para=para+"?page="+str(4)
