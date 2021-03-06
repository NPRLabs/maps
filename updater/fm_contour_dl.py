import argparse
import requests
import time
import sys
import math
from kml_to_geojson import parse_kml_to_dict, write_to_string
import sqlite3
import json


def load_from_website(callsign,appid,freq,city,state):

    payload = {
    'appid':appid,
    'call':callsign,
    'freq':freq,
    'contour':54,
    'city':city,
    'state':state,
    '.txt':''
    }

    url = 'https://transition.fcc.gov/fcc-bin/{}'.format('contourplot.kml')
    chunk_size = 1024
    r = requests.get(url, params=payload,stream=True)
    kml = r.text
    ses = kml.splitlines()
    return ses[0] + '\n<kml>' + '\n'.join(ses[2:])
    
def is_null_island(json):
    return testjs['geometries'][0]['geometry']['coordinates'][0] == 0.0 and
        testjs['geometries'][0]['geometry']['coordinates'][1] == 0.0
        
def fix_shift(testjs,lat, lon):
    for i,x in testjs['geometries'][1]['geometry']['coordinates']:
        new_c = [(x[0]+lon), (x[1]+lat)]
    if testjs['geometries'][1]['geometry']['coordinates'][i] = new_c
    testjs['geometries'][0]['geometry']['coordinates'] = [lon, lat]
    return testjs
    
def load_fm_contour(callsign,appid,freq,city,state, lat, lon):
    kml = load_from_website(callsign,appid,freq,city,state)
    testjs = parse_kml_to_dict(kml, None)
    if is_null_island(testjs)
        testjs = fix_shift(testjs,lat,lon)
    s = write_to_string(testjs, None)
    return s


if __name__ == '__main__':
    db = sqlite3.connect('fcc.db')
    cur = db.cursor()

    cur.execute('''SELECT id,callsign,appid,freq,city,state FROM fm WHERE
                    member NOT NULL and status=? and service=?''',('LIC', 'FM'))
    to_search = cur.fetchall()
    print 'Total: ' + str(len(to_search))
    for i, c in enumerate(to_search):
        print str(i) + ': ' + str(c[1])
        kml = load_from_website(c[1],c[2],c[3],c[4].replace(' ','_').upper(),c[5])
        s = write_to_string(parse_kml_to_dict(kml, None), None)
        cur.execute('''UPDATE fm SET con=? WHERE id=?''', (s, c[0]))

    
    db.commit()
    db.close()
  



