#!/usr/bin/python
import base64, getopt, json, os, StringIO as sio, sys, urllib2 as u, zipfile as z

opts=dict(getopt.getopt(sys.argv[1:], 'h:u:p:m:l:', ['proj='])[0])
auth={'Authorization':'Basic ' + base64.encodestring('%(-u)s:%(-p)s' % opts).strip()}

for exp in filter(lambda x: x['label'] not in os.listdir(opts['-l']), json.loads(u.urlopen(u.Request(url='%(-h)s/REST/projects/%(--proj)s/experiments' % opts, headers=auth)).read())['ResultSet']['Result']) :
        z.ZipFile(sio.StringIO(u.urlopen(u.Request(url=opts['-h'] + '%(URI)s/scans/ALL/files?format=zip' % exp, headers=auth)).read()), 'r').extractall(opts['-l'])
