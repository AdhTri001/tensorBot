"""
Enter your api key below for speech recognisation.
You can get one from https://azure.microsoft.com/en-ca/pricing/details/cognitive-services/speech-api/
Also mention the location of your service to speech recognisation to work.
"""

import pickle as pkl

pkl.dump(('YOUR_API_KEY', 'YOUR_API_LOCATION'), open('data/API.pkl', 'wb+'))

"""
Dont touch the bollow part. This will ready your database.
"""

import sqlite3 as sql

open('data/SideData.sqlite3', 'w+').close()

conn = sql.connect('data/SideData.sqlite3')
curs = conn.cursor()

curs.execute("""
CREATE TABLE IF NOT EXISTS timezones(
    country_code varchar(2),
    country_name varchar(4),
    country_city text
)
""")
curs.execute("""
CREATE TABLE IF NOT EXISTS notes(
    title varchar(20),
    descrption varchar(200),
    unix_ts numeric
)
""")
curs.executemany("""
INSERT INTO timezones VALUES(
    ?, ?, ?
)
""")

curs.close()
conn.close()