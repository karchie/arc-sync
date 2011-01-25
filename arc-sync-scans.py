#!/usr/bin/python
# arc-sync-scans.py
# Copyright (c) 2010,2011 Washington University
# Author: Kevin A. Archie <karchie@wustl.edu>
#
# Usage:
# arc-sync-scans \
#   -h ${XNAT_BASE_URL}  \
#   --proj ${XNAT_PROJECT} \    (NOTE preceding double dash)
#   -u ${XNAT_USER}      \
#   -p ${XNAT_PASSWORD}  \
#   -m ${REQUESTED_MODALITIES} \
#      (-m is optional; multiple values separated by commas) \
#   -l ${LOCAL_CACHE_DIR} \
#   -s ${REQUESTED_SCAN_TYPES} \
#      (-t is optional; multiple values separated by commas)

import base64, getopt, getpass, json, os, re, StringIO as sio, string, sys, urllib2 as u, zipfile as z

# Read and parse command-line arguments
optsl,args = getopt.getopt(sys.argv[1:], 'h:u:p:m:l:s:', ['proj='])
opts=dict(optsl)

# XNAT base URL can be either -h or the first non-option argument
base=opts['-h'] if '-h' in opts else args[0]

# XNAT user/pass can be -u/-p or prompted
user=opts['-u'] if '-u' in opts else raw_input('username: ')
passwd=opts['-p'] if '-p' in opts else getpass.getpass('password: ')

# Build HTTP header for Basic Authorization
auth={'Authorization':'Basic '+base64.encodestring(user+':'+passwd).strip()}

# Requested modalities
if '-m' in opts:
    xsitypes='xsiType=' + string.join(
        map(lambda m: 'xnat:' + m.lower() + 'SessionData',
            opts['-m'].split(','))) + '&'
else:
    xsitypes=''

# Local data cache
cache=opts['-l']

# Requested scan types
types=opts['-s'] if '-s' in opts else 'ALL'

# What sessions are already (at least partially) present in data cache?
existing=os.listdir(cache)

# Copy requested types into a list so we can look for matches
typelist=types.split(',')


def get(uri):
    """Retrieves the resource text from the given URI on the named host."""
    return u.urlopen(u.Request(url=base+uri, headers=auth)).read()

def getJSONResults(uri):
    """Retrieves the Result array from an XNAT JSON search result."""
    return json.loads(get(uri))['ResultSet']['Result']

def getScanFiles(expt, scans):
    """Retrieves the data files for the given scan names or types from
the given experiment."""
    args = {'URI':expt['URI'], 'scans':scans}
    z.ZipFile(sio.StringIO(get('%(URI)s/scans/%(scans)s/files?format=zip' % args)), 'r').extractall(cache)


# main
for expt in getJSONResults('/REST/projects/%(--proj)s/experiments' % opts):
    label = expt['label']
    if label not in existing:
        getScanFiles(expt, types)
    else:
        for scan in getJSONResults('%(URI)s/scans' % expt):
            if types == 'ALL' or scan['type'] in typelist:
                name=re.sub(r'[^\w\-]', '_', "%(ID)s-%(type)s" % scan)
                if name not in os.listdir(cache+'/'+label+'/scans'):
                    getScanFiles(expt, scan['ID'])