#!/usr/bin/python3

"""
An interesting way to use the data grabbed from the WiGLE API.

officeTasks may be found at:
    https://github.com/stryngs/officeTasks
"""
import geoplotlib as gp
import officeTasks as OT
import pandas as pd
import random
import requests
import sqlite3 as lite
import time
from configparser import ConfigParser
from pandas.io.json import json_normalize
from requests.auth import HTTPBasicAuth

def curlEm(bLat, tLat, lLong, rLong):
    ## wigle work
    payload = {'latrange1':bLat, 'latrange2':tLat, 'longrange1':str(lLong), 'longrange2':str(rLong), 'api_key': (api_name + api_token).encode()}
    req = requests.get(url='https://api.wigle.net/api/v2/network/search', params=payload, auth=HTTPBasicAuth(api_name, api_token))
    ourResults = req.json()

    if req.status_code == 200:
        if ourResults.get('success') == False:
            print(ourResults.get('message'))
            return None, None
        else:

            ## Results
            pResults = ourResults.get('results')
            print('Done! -- obj is pResults')
            return pResults, req.status_code


def dbPrep():
    """Connect and prep the db"""
    sqlName ='wigle.sqlite3'
    dbName = 'wigle'
    con = lite.connect(sqlName)
    db = con.cursor()

    ## sqlite3 table create
    db.execute("""
               CREATE TABLE IF NOT EXISTS {0}(bcninterval TEXT,
                                              channel INTEGER,
                                              city TEXT,
                                              comment TEXT,
                                              country TEXT,
                                              dhcp TEXT,
                                              encryption TEXT,
                                              firsttime TEXT,
                                              freenet TEXT,
                                              housenumber TEXT,
                                              lasttime TEXT,
                                              lastupdt TEXT,
                                              name TEXT,
                                              netid TEXT,
                                              paynet TEXT,
                                              postalcode INTEGER,
                                              qos INTEGER,
                                              region TEXT,
                                              road TEXT,
                                              ssid TEXT,
                                              transid TEXT,
                                              trilat REAL,
                                              trilong REAL,
                                              type TEXT,
                                              userfound TEXT,
                                              wep TEXT);
               """.format(dbName))
    return (con, db, dbName)


def dbUpdate(dObj):
    """Takes the iterated dict from the list and parses it for sql"""
    bcninterval = dObj.get('bcninterval')
    channel = dObj.get('channel')
    city = dObj.get('city')
    comment = dObj.get('comment')
    country = dObj.get('count')
    dhcp = dObj.get('country')
    encryption = dObj.get('encryption')
    firsttime = dObj.get('firsttime')
    freenet = dObj.get('freenet')
    housenumber = dObj.get('housenumber')
    lasttime = dObj.get('lasttime')
    lastupdt = dObj.get('lastupdt')
    name = dObj.get('name')
    netid = dObj.get('netid')
    paynet = dObj.get('paynet')
    postalcode = dObj.get('postalcode')
    qos = dObj.get('qos')
    region = dObj.get('region')
    road = dObj.get('road')
    ssid = dObj.get('ssid')
    transid = dObj.get('transid')
    trilat = dObj.get('trilat')
    trilong = dObj.get('trilong')
    type = dObj.get('type')
    userfound = dObj.get('userfound')
    wep = dObj.get('wep')

    ## db Update
    db.execute("""
               INSERT INTO `{0}` VALUES(?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?,
                                        ?);
               """.format(dbName), (bcninterval,
                                    channel,
                                    city,
                                    comment,
                                    country,
                                    dhcp,
                                    encryption,
                                    firsttime,
                                    freenet,
                                    housenumber,
                                    lasttime,
                                    lastupdt,
                                    name,
                                    netid,
                                    paynet,
                                    postalcode,
                                    qos,
                                    region,
                                    road,
                                    ssid,
                                    transid,
                                    trilat,
                                    trilong,
                                    type,
                                    userfound,
                                    wep))

if __name__ == '__main__':

    ## fs prep
    OT.gnr.sweep('wigle.csv')

    ## creds
    parser = ConfigParser()
    psr = parser.read('wigle.ini')
    api_name = parser.get('creds', 'api_name')
    api_token = parser.get('creds', 'api_token')

    ## bounding
    bLat =  parser.get('loc', 'bLat')
    tLat =  parser.get('loc', 'tLat')
    lLong = parser.get('loc', 'lLong')
    rLong = parser.get('loc', 'rLong')
    iCre =  parser.get('loc', 'iCre') # negative for going left about the map
    bLat = float(bLat)
    tLat = float(tLat)
    lLong = float(lLong)
    rLong = float(rLong)
    iCre = float(iCre)

    ## db connection
    con, db, dbName = dbPrep()

    ## Grab!
    token = parser.get('loc', 'token')
    for i in range(int(token)):
        print('Starting - {0}'.format(i))
        lLong += iCre
        rLong += iCre
        pResults, status_code = curlEm(bLat, tLat, lLong, rLong)
        if status_code is not None:
            if pResults is not None:
                for i in pResults:
                    try:
                        dbUpdate(i)
                        con.commit()
                    except Exception as E:
                        print(E)
                print('Sleeping')
            else:
                print('http status code: {0}'.format(status_code))
        sVal = random.randint(1, 2)
        print('sleeping for {0}'.format(sVal))
        time.sleep(sVal)
        print('waking\n')

    ## Get column names
    q = db.execute("""
                   PRAGMA TABLE_INFO(wigle);
                   """)
    r = q.fetchall()
    hdrs = []
    for i in r:
        hdrs.append(i[1])

    ## Get rows
    q = db.execute("""
                   SELECT * FROM wigle;
                   """)
    r = q.fetchall()

    ## Close db
    con.close()

    ## CSV the wigle table
    OT.csv.csvGen('wigle.csv', headers = hdrs, rows = r)
    print('[+] wigle.csv has been generated\n')
