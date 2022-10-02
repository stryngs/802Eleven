#!/usr/bin/python3

import officeTasks as OT
import psycopg2
from configparser import ConfigParser

def dbUpdater(row):

    if not isinstance(row[1], int):
        row[1] = None
    if not isinstance(row[15], int):
        row[15] = None
    if not isinstance(row[16], int):
        row[16] = None
    if not isinstance(row[21], float):
        row[21] = None
    if not isinstance(row[22], float):
        row[22] = None


    db.execute("""
            INSERT INTO {0} (bcninterval,
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
                            wep)
                            VALUES (%s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s,
                                    %s);
            """.format('wigle'),
                (row[0],
                (row[1]),
                 row[2],
                 row[3],
                 row[4],
                 row[5],
                 row[6],
                 row[7],
                 row[8],
                 row[9],
                 row[10],
                 row[11],
                 row[12],
                 row[13],
                 row[14],
                 row[15],
                 row[16],
                 row[17],
                 row[18],
                 row[19],
                 row[20],
                 row[21],
                 row[22],
                 row[23],
                 row[24],
                 row[25]))

if __name__ == '__main__':
    ## creds
    parser = ConfigParser()
    psr = parser.read('wigle.ini')
    host = parser.get('idrop', 'host')
    dbname = parser.get('idrop', 'dbname')
    user = parser.get('idrop', 'user')
    password = parser.get('idrop', 'password')

    con = psycopg2.connect(host = host,
                           dbname = dbname,
                           user = user,
                           password = password)

    ## auto commits
    con.autocommit = True
    #create a cursor object
    #cursor object is used to interact with the database
    db = con.cursor()

    ## prep table
    db.execute("""
               CREATE TABLE IF NOT EXISTS wigle(bcninterval TEXT,
                                                channel INT,
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
                                                postalcode INT,
                                                qos INT,
                                                region TEXT,
                                                road TEXT,
                                                ssid TEXT,
                                                transid TEXT,
                                                trilat REAL,
                                                trilong REAL,
                                                type TEXT,
                                                userfound TEXT,
                                                wep TEXT);
               """)

    ## list the csv && remove hdr
    ourCsv = OT.csv.csv2list('wigle.csv')
    ourCsv.pop(0)

    ## Rip through rows
    count = 0
    for row in ourCsv:
        print('Row: {0}/{1}'.format(count, len(ourCsv)))
        try:
            dbUpdater(row)
        except Exception as E:
            print(E)
        count += 1

    ## closeout
    con.close()
    print('idrop wigle table updated\n')
