#! /usr/bin/env python3

import sys
import requests
from bs4 import BeautifulSoup

content = requests.get('https://www.dvb.de/de-de/fahrplan/haltestellenauskunft/haltestellenkuerzel/').text
soup = BeautifulSoup(content, 'html.parser')

tables = soup.find_all('table')

if len(sys.argv) != 2:
    print('`dresden` or `umland`?')
    sys.exit(1)

if sys.argv[1].lower() == 'dresden':
    for table in tables[0:2]:
        for tr in table.find_all('tr')[1:]:
            tds = tr.find_all('td')
            name, kuerzel = tds
            print('{};{}'.format(name.text.strip(),
                                 kuerzel.text.strip()))
elif sys.argv[1].lower() == 'umland':
    for tr in tables[2].find_all('tr')[1:]:
        tds = tr.find_all('td')
        ort, name, kuerzel = tds
        print('{}, {};{}'.format(name.text.strip(),
                                 ort.text.strip(),
                                 kuerzel.text.strip()))
else:
    print('`dresden` or `umland`?')
    sys.exit(1)
