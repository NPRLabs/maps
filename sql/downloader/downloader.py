import argparse
import requests
import time
import sys
import math


def setup_args():
    parser = argparse.ArgumentParser(description='small tool')


    parser.add_argument('which', choices=['tv', 'am', 'fm'])
    parser.add_argument('-o', '--output-file', default='', dest='outfile')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-r', '--reload_from_source', action='store_true')
    group.add_argument('-s', '--load_file', default='', dest='filename')

    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument('-q', '--query', nargs=2, default='', dest='query')
    group2.add_argument('-l', '--listquery', nargs=2, default='', dest='listquery')
    group2.add_argument('-f', '--filter', help='1:field filter by 2: value it must be, 3:new filename', nargs=3, default='', dest='filt')

    return parser

def format_line(line):
    
        vals = line.split('|')
        if not vals[0]:
            vals.pop(0)
        return '|'.join(map(str.strip,vals))

def load_from_website(args, filename, callsign):
    stdout = (not filename) or filename == '-'
    print 'FILENAME'
    print filename
    f = None
    if not stdout:
        print 'yep'
        f = open(filename, 'wb')

    r = requests.get('https://api.github.com/events')

    payload = {'call':'',
    'arn':'',
    'state':'',
    'city':'',
    'serv':'',
    'vac':'',
    'facid':'',
    'asrn':'',
    'class':'',
    'list':'4',
    'ThisTab':'Results+to+This+Page%2FTab',
    'dist':'',
    'dlat2':'',
    'mlat2':'',
    'slat2':'',
    'NS':'N',
    'dlon2':'',
    'mlon2':'',
    'slon2':'',
    'EW':'W',
    'size':9}

    
    if args.which == 'tv':
        payload['chan'] = '0.0'
        payload['cha2'] = '69'
    elif args.which == 'fm':
        payload['freq'] = '0.0'
        payload['fre2'] = '107.9'
    else:
        payload['freq'] = '530'
        payload['fre2'] = '1700'


    url = 'https://transition.fcc.gov/fcc-bin/{}q'.format(args.which)
    print 'Url to use:{}'.format(url)
    chunk_size = 1024
    r = requests.get(url, params=payload, stream=True)
    print r.url
    count = 0
    for line in r.iter_lines(chunk_size):
        
        # the data is gross so we need to do this
        line = format_line(line)
        count += 1
        
        if line: 
            if stdout:
                print line
            else:
                f.write(line + '\n')
        print 'Count:{}'.format(count)
        
    if not stdout:
        f.close()

def call_q(line, value):
    l = line.split(',')
    return value.lower() == l[0].lower()


def freq_q(line, value):
    l = line.split(',')
    return abs(float(value) - float(l[1].split()[0])) < .0001

def type_q(line, value):
    l = line.split(',')
    return l[2] == value

def lic_q(line, value):
    l = line.split(',')
    return l[4] == value

def query_file(filename, value, option):
    f = open(filename, 'r')
    query_func = None
    if option == 'callsign':
        query_func = call_q
    elif option == 'freq':
        query_func = freq_q

    for line in f:
        if line:
#            for entry in filter(lambda l: callsign in l, line.split(',')):
#                if entry:
#                    sys.stdout.write(line)
            if query_func(line, value):
                sys.stdout.write(line)
                
    f.close()

def filter_by(src, dest, value, option):
    f = open(src, 'r')
    f2 = open(dest, 'w')
    query_func = None
    if option == 'callsign':
        query_func = call_q
    elif option == 'freq':
        query_func = freq_q
    elif option == 'type':
        query_func = type_q
    elif option == 'license':
        query_func = lic_q

    for line in f:
        if line:
#            for entry in filter(lambda l: callsign in l, line.split(',')):
#                if entry:
#                    sys.stdout.write(line)
            if query_func(line, value):
                f2.write(line)
    f.close()
    f2.close()


if __name__ == '__main__':
    parser = setup_args()
    args = parser.parse_args()
    if args.reload_from_source:
        load_from_website(args, args.outfile, None)
    filename = None
    if args.filename:
        filename = args.filename
    else:
        filename = 'data/{}_data.txt'.format(args.which)
    if args.query:
        print 'good'
        query_file(filename, args.query[1],args.query[0])
    elif args.listquery:
        fl = open(args.listquery[1], 'r')
        print args.listquery
        for line in fl:
            print 'AAA{}AAA'.format(line)
            print 'Query for: {}'.format(line)
            query_file(filename, line.rstrip(), args.listquery[0])
            print 
    elif args.filt:
        print args.filt
        filter_by(filename, args.filt[2], args.filt[1], args.filt[0]) 

  



