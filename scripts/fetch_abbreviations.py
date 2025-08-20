#! /usr/bin/env python3

# /// script
# dependencies = [
#   "requests<3",
#   "beautifulsoup4<5",
#   "pypdf2",
# ]
# ///

import sys
import os
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io
import re
from urllib.parse import urljoin

def fetch_pdf():
    """Fetch the PDF from DVB website"""
    url = 'https://www.dvb.de/de-de/fahrplan/haltestellenauskunft/haltestellenkuerzel/'
    print(f"Fetching DVB page from {url}...", file=sys.stderr)
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    pdf_link = None
    for link in soup.find_all('a', href=True):
        if '.pdf' in link['href'].lower() and 'haltestellenliste' in link['href'].lower():
            pdf_link = urljoin(url, link['href'])
            break
    
    if not pdf_link:
        print("Error: Could not find PDF link on the page", file=sys.stderr)
        sys.exit(1)
    
    print(f"Downloading PDF from {pdf_link}...", file=sys.stderr)
    pdf_response = requests.get(pdf_link)
    if pdf_response.status_code != 200:
        print(f"Error: Could not download PDF from {pdf_link}", file=sys.stderr)
        sys.exit(1)
    
    return pdf_response.content

def extract_abbreviations(pdf_content):
    """Extract station abbreviations from PDF"""
    pdf_file = io.BytesIO(pdf_content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    
    full_text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        full_text += page.extract_text() + "\n"
    
    dresden_stations = []
    regional_stations = []
    
    lines = full_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if 'Haltestelle' in line and 'Abkürzung' in line:
            continue
        
        if 'Ort' == line:
            continue
        
        parts = line.split()
        
        # Process Dresden stations
        if 'Dresden' in line:
            dresden_indices = [i for i, part in enumerate(parts) if part == 'Dresden']
            
            for idx in dresden_indices:
                for j in range(idx + 1, len(parts)):
                    if re.match(r'^[A-Z0-9]{2,4}$', parts[j]):
                        kuerzel = parts[j]
                        name_parts = parts[idx+1:j]
                        if name_parts:
                            name = ' '.join(name_parts)
                            dresden_stations.append(f'{name};{kuerzel}')
                        break
        
        # Process regional (non-Dresden) stations
        elif not line.startswith('Dresden '):
            abbreviations = []
            abbrev_indices = []
            
            for i in range(len(parts)):
                if re.match(r'^[A-Z0-9]{2,4}$', parts[i]):
                    abbreviations.append(parts[i])
                    abbrev_indices.append(i)
            
            if abbreviations:
                first_abbrev_idx = abbrev_indices[0]
                
                if first_abbrev_idx >= 2:
                    before_abbrev = parts[:first_abbrev_idx]
                    
                    ort = ""
                    halt_start_idx = 1
                    
                    if len(before_abbrev) > 0:
                        if '(' in ' '.join(before_abbrev):
                            for j, part in enumerate(before_abbrev):
                                if ')' in part:
                                    ort = ' '.join(before_abbrev[:j+1])
                                    halt_start_idx = j + 1
                                    break
                        else:
                            ort = before_abbrev[0]
                            halt_start_idx = 1
                    
                    if halt_start_idx < first_abbrev_idx:
                        haltestelle = ' '.join(before_abbrev[halt_start_idx:])
                        
                        for abbrev in abbreviations:
                            if haltestelle and ort:
                                regional_stations.append(f'{haltestelle}, {ort};{abbrev}')
                            elif haltestelle:
                                regional_stations.append(f'{haltestelle};{abbrev}')
                elif first_abbrev_idx == 1:
                    if parts[0] == parts[1]:
                        regional_stations.append(f'{parts[0]}, {parts[0]};{abbreviations[0]}')
                    else:
                        regional_stations.append(f'{parts[0]};{abbreviations[0]}')
    
    return dresden_stations, regional_stations

def main():
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Fetch and process PDF
    pdf_content = fetch_pdf()
    dresden_stations, regional_stations = extract_abbreviations(pdf_content)
    
    # Write Dresden stations
    dresden_file = os.path.join(data_dir, 'abbreviations_dresden.csv')
    with open(dresden_file, 'w', encoding='utf-8') as f:
        for station in dresden_stations:
            f.write(station + '\n')
    print(f"Wrote {len(dresden_stations)} Dresden stations to {dresden_file}", file=sys.stderr)
    
    # Write regional stations
    regional_file = os.path.join(data_dir, 'abbreviations_regional.csv')
    with open(regional_file, 'w', encoding='utf-8') as f:
        for station in regional_stations:
            f.write(station + '\n')
    print(f"Wrote {len(regional_stations)} regional stations to {regional_file}", file=sys.stderr)
    
    print("\nDone! Generated:", file=sys.stderr)
    print("  - abbreviations_dresden.csv", file=sys.stderr)
    print("  - abbreviations_regional.csv", file=sys.stderr)

if __name__ == "__main__":
    main()
