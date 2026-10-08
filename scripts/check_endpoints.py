#!/usr/bin/env python3

# /// script
# dependencies = []
# ///

"""Check every documented endpoint once and append the result to a JSON history.

Usage:
    python check_endpoints.py <history.json>

The history keeps one sample per run for the last 30 days. The status site reads it
to show current state and uptime. A check that answers but returns stale data counts
as degraded, since a frozen feed breaks consumers as much as an outage does.
"""

import base64
import http.client
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

RETENTION = timedelta(days=30)
TIMEOUT = 30
UP, DOWN, DEGRADED = 1, 0, 2
HOUR = 3600
DAY = 24 * HOUR

WEBAPI = "https://webapi.vvo-online.de"
WIDGETS = "http://widgets.vvo-online.de/abfahrtsmonitor"

TRIAS_LIR = """<?xml version="1.0" encoding="UTF-8"?>
<Trias xmlns="trias" xmlns:siri="http://www.siri.org.uk/siri" version="1.2">
  <ServiceRequest>
    <siri:RequestTimestamp>{now}</siri:RequestTimestamp>
    <siri:RequestorRef>OpenService</siri:RequestorRef>
    <RequestPayload>
      <LocationInformationRequest>
        <InitialInput><LocationName>Hauptbahnhof</LocationName></InitialInput>
        <Restrictions><Type>stop</Type><NumberOfResults>1</NumberOfResults></Restrictions>
      </LocationInformationRequest>
    </RequestPayload>
  </ServiceRequest>
</Trias>"""


def webapi(path, body):
    return {"url": f"{WEBAPI}/{path}", "json": {**body, "format": "json"}, "expect": "Status"}


# `docs` is the path of the matching page on the status site, `max_age` the allowed Last-Modified age.
CHECKS = [
    {"id": "webapi-pointfinder", "group": "WebAPI", "name": "PointFinder", "docs": "docs/webapi/#pointfinder",
     **webapi("tr/pointfinder", {"query": "Postplatz", "limit": 1, "stopsOnly": True})},
    {"id": "webapi-dm", "group": "WebAPI", "name": "Departure monitor", "docs": "docs/webapi/#departure-monitor",
     **webapi("dm", {"stopid": "33000028", "limit": 1})},
    {"id": "webapi-trips", "group": "WebAPI", "name": "Trip query", "docs": "docs/webapi/#query-a-trip",
     **webapi("tr/trips", {"origin": "33000028", "destination": "33000016"})},
    {"id": "webapi-rc", "group": "WebAPI", "name": "Route changes", "docs": "docs/webapi/#route-changes",
     **webapi("rc", {"shortterm": True})},
    {"id": "webapi-lines", "group": "WebAPI", "name": "Lines", "docs": "docs/webapi/#lines",
     **webapi("stt/lines", {"stopid": "33000028"})},
    {"id": "widgets-departures", "group": "Widget API", "name": "Abfahrten", "docs": "docs/widgets/#abfahrten",
     "url": f"{WIDGETS}/Abfahrten.do?hst=Hauptbahnhof&ort=Dresden&lim=1", "expect": "["},
    {"id": "widgets-stops", "group": "Widget API", "name": "Haltestelle", "docs": "docs/widgets/#haltestelle",
     "url": f"{WIDGETS}/Haltestelle.do?hst=Postplatz&ort=Dresden", "expect": "["},
    {"id": "trias", "group": "TRIAS", "name": "LocationInformationRequest", "docs": "docs/trias/",
     "url": "http://efa.vvo-online.de:8080/std3/trias", "xml": TRIAS_LIR, "expect": "LocationResult"},
    {"id": "gtfs-static", "group": "GTFS", "name": "gtfs.de local transit feed", "docs": "docs/gtfs/",
     "url": "https://download.gtfs.de/germany/nv_free/latest.zip", "head": True, "max_age": 8 * DAY},
    {"id": "gtfs-rt", "group": "GTFS", "name": "gtfs.de realtime feed", "docs": "docs/gtfs/#gtfs-realtime",
     "url": "https://realtime.gtfs.de/realtime-free.pb", "head": True, "max_age": HOUR},
    {"id": "siri-mirror", "group": "SIRI ET", "name": "Oberelbe mirror", "docs": "docs/siri/",
     "url": "https://stc.traines.eu/mirror/german-delfi-siri/oberelbe/latest-oberelbe.siri.xml", "head": True,
     "max_age": HOUR},
    {"id": "vvo-stops", "group": "VVO open data", "name": "VVO_STOPS.JSON", "docs": "downloads/",
     "url": "https://www.vvo-online.de/open_data/VVO_STOPS.JSON", "head": True, "max_age": 3 * DAY},
    {"id": "vvo-pur", "group": "VVO open data", "name": "PuR.JSON", "docs": "downloads/",
     "url": "https://www.vvo-online.de/open_data/PuR.JSON", "head": True},
    {"id": "opendata", "group": "Dresden OpenData", "name": "OGC API collections", "docs": "docs/opendata/",
     "url": "https://kommisdd.dresden.de/net4/public/ogcapi/collections?f=json", "expect": "collections"},
    {"id": "tlms", "group": "TLMS", "name": "WebSocket", "docs": "docs/tlms/",
     "url": "https://socket.tlm.solutions/", "websocket": True},
]


def run(check):
    """Returns (status, milliseconds, note)."""
    start = time.monotonic()
    try:
        if check.get("websocket"):
            return websocket_handshake(check["url"], start)
        headers = {"User-Agent": "kiliankoe/vvo endpoint health check (+https://github.com/kiliankoe/vvo)"}
        data = None
        if "json" in check:
            data = json.dumps(check["json"]).encode()
            headers["Content-Type"] = "application/json; charset=utf-8"
        elif "xml" in check:
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            data = check["xml"].format(now=now).encode()
            headers["Content-Type"] = "text/xml; charset=utf-8"
        method = "HEAD" if check.get("head") else ("POST" if data else "GET")
        req = urllib.request.Request(check["url"], data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            body = b"" if method == "HEAD" else res.read(2_000_000)
            ms = elapsed(start)
            if check.get("expect") and check["expect"].encode() not in body:
                return DOWN, ms, "unexpected response"
            if check.get("max_age") and res.headers.get("Last-Modified"):
                age = datetime.now(timezone.utc) - parsedate_to_datetime(res.headers["Last-Modified"])
                if age.total_seconds() > check["max_age"]:
                    return DEGRADED, ms, f"data is {format_age(age)} old"
            return UP, ms, None
    except urllib.error.HTTPError as e:
        return DOWN, elapsed(start), f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001 - any failure means the endpoint is unusable
        return DOWN, elapsed(start), type(e).__name__


def websocket_handshake(url, start):
    host = url.split("/")[2]
    conn = http.client.HTTPSConnection(host, timeout=TIMEOUT)
    conn.request("GET", "/", headers={
        "Upgrade": "websocket",
        "Connection": "Upgrade",
        "Sec-WebSocket-Key": base64.b64encode(os.urandom(16)).decode(),
        "Sec-WebSocket-Version": "13",
    })
    status = conn.getresponse().status
    conn.close()
    return (UP, elapsed(start), None) if status == 101 else (DOWN, elapsed(start), f"HTTP {status}")


def elapsed(start):
    return round((time.monotonic() - start) * 1000)


def format_age(age):
    return f"{age.days} days" if age.days else f"{round(age.total_seconds() / HOUR)} hours"


def main():
    path = sys.argv[1]
    try:
        with open(path) as f:
            history = json.load(f)
    except FileNotFoundError:
        history = {"samples": []}

    now = datetime.now(timezone.utc)
    results = {}
    for check in CHECKS:
        status, ms, note = run(check)
        results[check["id"]] = [status, ms, note] if note else [status, ms]
        print(f"{check['id']}: {['down', 'up', 'degraded'][status]} {ms} ms {note or ''}", file=sys.stderr)

    cutoff = now - RETENTION
    samples = [s for s in history["samples"] if datetime.fromisoformat(s["t"]) >= cutoff]
    samples.append({"t": now.isoformat(timespec="seconds"), "r": results})
    keys = ("id", "group", "name", "docs", "url")
    history = {
        "checks": [{k: c[k] for k in keys} for c in CHECKS],
        "samples": samples,
    }
    with open(path, "w") as f:
        json.dump(history, f, separators=(",", ":"), ensure_ascii=False)


if __name__ == "__main__":
    main()
