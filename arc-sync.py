#!/usr/bin/python
import base64, getopt, json, os, StringIO as sio, sys, urllib2 as u, zipfile as z

opts=dict(getopt.getopt(sys.argv[1:], 'h:u:p:m:l:', ['proj='])[0])

def get(url): return u.urlopen(u.Request(url=opts['-h']+url, headers={'Authorization':'Basic '+base64.encodestring('%(-u)s:%(-p)s' % opts).strip()})).read()

map(lambda e: z.ZipFile(sio.StringIO(get('%(URI)s/scans/ALL/files?format=zip' % e)), 'r').extractall(opts['-l']), filter(lambda x: x['label'] not in os.listdir(opts['-l']), json.loads(get('/REST/projects/%(--proj)s/experiments' % opts))['ResultSet']['Result']))
