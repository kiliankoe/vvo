#!/usr/bin/env python3

# /// script
# dependencies = []
# ///

"""Build a VVO-area GTFS subset and a per-line service summary.

gtfs.de publishes no VVO feed, so this cuts one out of the Germany-wide local
transit feed: every trip that touches a stop inside the bounding box of the
stations in data/stations.json is kept in full, together with everything it
references.

The summary is meant to be committed, so it avoids feed-internal IDs and
absolute dates, which change between feed versions without any real change
in service.
"""

import argparse
import csv
import datetime
import io
import json
import re
import statistics
import sys
import tempfile
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

FEED_URL = "https://download.gtfs.de/germany/nv_free/latest.zip"

# Files we know how to subset or copy. Anything else in the feed would likely
# reference IDs we drop, so it is skipped with a warning.
KNOWN_FILES = {
    "agency.txt", "attributions.txt", "calendar.txt", "calendar_dates.txt",
    "feed_info.txt", "routes.txt", "stop_times.txt", "stops.txt", "trips.txt",
}

ROUTE_TYPES = {
    "0": "Tram", "1": "Subway", "2": "Rail", "3": "Bus", "4": "Ferry",
    "5": "Cable tram", "6": "Aerial lift", "7": "Funicular",
    "11": "Trolleybus", "12": "Monorail",
}

WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
SUMMARY_FIELDS = ["agency", "line", "type", *WEEKDAYS,
                  "first_departure", "last_departure", "stops"]


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def download(url, dest):
    log(f"Downloading {url}...")
    req = urllib.request.Request(url, headers={"User-Agent": "kiliankoe/vvo"})
    with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
        while chunk := resp.read(1 << 20):
            f.write(chunk)


def station_bbox(path):
    stations = json.loads(Path(path).read_text(encoding="utf-8"))["stations"]
    lats = [s["latitude"] for s in stations if s.get("latitude")]
    lons = [s["longitude"] for s in stations if s.get("longitude")]
    return min(lats), max(lats), min(lons), max(lons)


def read_text(zf, name):
    # utf-8-sig tolerates a BOM, which some GTFS producers emit.
    return io.TextIOWrapper(zf.open(name), encoding="utf-8-sig", newline="")


def write_text(out, name):
    return io.TextIOWrapper(out.open(name, "w", force_zip64=True),
                            encoding="utf-8", newline="")


def filter_csv(zf, out, name, keep):
    """Copy rows of `name` for which keep(row) is true; return the kept rows."""
    kept = []
    with read_text(zf, name) as src, write_text(out, name) as dst:
        reader = csv.DictReader(src)
        writer = csv.DictWriter(dst, reader.fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in reader:
            if keep(row):
                writer.writerow(row)
                kept.append(row)
    return kept


def subset_stop_times(zf, out, in_bbox):
    """Copy the stop_times of trips that touch a stop in the bounding box.

    This file is ~2 GB, so it is streamed as raw lines and only the leading
    columns are split. Rows are grouped by trip in gtfs.de feeds, which lets
    us decide per trip in a single pass.
    """
    trips = {}  # trip_id -> (first departure, set of stop_ids)
    seen = set()
    with read_text(zf, "stop_times.txt") as src, \
            write_text(out, "stop_times.txt") as dst:
        header = src.readline()
        dst.write(header)
        cols = next(csv.reader([header]))
        i_trip, i_dep, i_stop, i_seq = (cols.index(c) for c in (
            "trip_id", "departure_time", "stop_id", "stop_sequence"))
        nsplit = max(i_trip, i_dep, i_stop, i_seq) + 1

        def flush(trip_id, lines, rows):
            if trip_id in seen:
                sys.exit(f"stop_times.txt is not grouped by trip ({trip_id})")
            seen.add(trip_id)
            stops = {r[i_stop] for r in rows}
            if stops & in_bbox:
                dst.writelines(lines)
                first = min(rows, key=lambda r: int(r[i_seq]))
                trips[trip_id] = (first[i_dep], stops)

        current, lines, rows = None, [], []
        for line in src:
            if not line.endswith("\n"):
                line += "\n"
            # Strip the terminator so it can't end up in the last split field.
            fields = line.rstrip("\r\n")
            parts = fields.split(",", nsplit)
            if any('"' in p for p in parts[:nsplit]):
                parts = next(csv.reader([fields]))
            if parts[i_trip] != current:
                if current is not None:
                    flush(current, lines, rows)
                current, lines, rows = parts[i_trip], [], []
            lines.append(line)
            rows.append(parts)
        if current is not None:
            flush(current, lines, rows)
    return trips


def build_subset(feed_path, out_path, bbox):
    lat_min, lat_max, lon_min, lon_max = bbox
    with zipfile.ZipFile(feed_path) as zf, \
            zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as out:
        for name in sorted(set(zf.namelist()) - KNOWN_FILES):
            log(f"Warning: skipping unknown feed file {name}")

        with read_text(zf, "stops.txt") as f:
            all_stops = list(csv.DictReader(f))
        in_bbox = {
            s["stop_id"] for s in all_stops
            if s["stop_lat"] and s["stop_lon"]
            and lat_min <= float(s["stop_lat"]) <= lat_max
            and lon_min <= float(s["stop_lon"]) <= lon_max
        }
        log(f"{len(in_bbox)} stops in bounding box, scanning stop_times...")

        trip_info = subset_stop_times(zf, out, in_bbox)
        log(f"Kept {len(trip_info)} trips")
        if not trip_info:
            sys.exit("No trips touch the bounding box, refusing to publish")

        trips = filter_csv(zf, out, "trips.txt",
                           lambda r: r["trip_id"] in trip_info)
        route_ids = {t["route_id"] for t in trips}
        service_ids = {t["service_id"] for t in trips}
        routes = filter_csv(zf, out, "routes.txt",
                            lambda r: r["route_id"] in route_ids)
        agency_ids = {r["agency_id"] for r in routes}
        agencies = filter_csv(zf, out, "agency.txt",
                              lambda r: r["agency_id"] in agency_ids)
        calendar = filter_csv(zf, out, "calendar.txt",
                              lambda r: r["service_id"] in service_ids)
        calendar_dates = filter_csv(zf, out, "calendar_dates.txt",
                                    lambda r: r["service_id"] in service_ids)

        stop_ids = set().union(*(stops for _, stops in trip_info.values()))
        parent = {s["stop_id"]: s["parent_station"] for s in all_stops}
        stop_ids |= {parent[s] for s in stop_ids if parent.get(s)}
        filter_csv(zf, out, "stops.txt", lambda r: r["stop_id"] in stop_ids)

        # Attribution is required by the license, so these are copied as is.
        for name in ("feed_info.txt", "attributions.txt"):
            if name in zf.namelist():
                out.writestr(name, zf.read(name))

    return {
        "trip_info": trip_info, "trips": trips, "routes": routes,
        "agencies": agencies, "calendar": calendar,
        "calendar_dates": calendar_dates, "parent": parent,
    }


def parse_date(s):
    return datetime.datetime.strptime(s, "%Y%m%d").date()


def service_dates(calendar, calendar_dates):
    dates = defaultdict(set)
    for c in calendar:
        day = parse_date(c["start_date"])
        end = parse_date(c["end_date"])
        runs = [c[d] == "1" for d in ("monday", "tuesday", "wednesday",
                "thursday", "friday", "saturday", "sunday")]
        while day <= end:
            if runs[day.weekday()]:
                dates[c["service_id"]].add(day)
            day += datetime.timedelta(days=1)
    for c in calendar_dates:
        day = parse_date(c["date"])
        if c["exception_type"] == "1":
            dates[c["service_id"]].add(day)
        else:
            dates[c["service_id"]].discard(day)
    return dates


def natural_key(s):
    return [(0, int(p), "") if p.isdigit() else (1, 0, p)
            for p in re.split(r"(\d+)", s) if p]


def summarize(subset):
    """One row per line with its typical number of trips per weekday.

    "Typical" is the upper median over all dates of that weekday in the feed
    window, so a single holiday does not move it. Lines where all of these
    are zero are left out, and departures and stops prefer regular trips,
    i.e. those running on more than half of the dates of some weekday. This
    keeps one-off services from adding noise as the window moves.
    """
    dates = service_dates(subset["calendar"], subset["calendar_dates"])
    all_dates = set().union(*dates.values())
    window = (min(all_dates), max(all_dates))
    agency_name = {a["agency_id"]: a["agency_name"]
                   for a in subset["agencies"]}
    route_key = {
        r["route_id"]: (agency_name[r["agency_id"]], r["route_short_name"]
                        or r["route_long_name"],
                        ROUTE_TYPES.get(r["route_type"], r["route_type"]))
        for r in subset["routes"]
    }
    parent = subset["parent"]

    by_weekday = [[] for _ in range(7)]
    day = window[0]
    while day <= window[1]:
        by_weekday[day.weekday()].append(day)
        day += datetime.timedelta(days=1)

    per_date = defaultdict(lambda: defaultdict(int))
    # Per line: trips as (is_regular, first departure, stop_ids)
    line_trips = defaultdict(list)
    for t in subset["trips"]:
        days = dates.get(t["service_id"])
        if not days:
            continue
        key = route_key[t["route_id"]]
        runs = [0] * 7
        for day in days:
            per_date[key][day] += 1
            runs[day.weekday()] += 1
        regular = any(2 * n > len(d) for n, d in zip(runs, by_weekday))
        line_trips[key].append((regular, *subset["trip_info"][t["trip_id"]]))

    rows = []
    for key in sorted(per_date, key=lambda k: (k[0], k[2], natural_key(k[1]))):
        typical = {name: statistics.median_high(
                       [per_date[key].get(d, 0) for d in by_weekday[wd]])
                   for wd, name in enumerate(WEEKDAYS)}
        if not any(typical.values()):
            continue
        # Lines without a single regular trip can still have a typical
        # count, e.g. when every school day uses a different service.
        trips = [t for t in line_trips[key] if t[0]] or line_trips[key]
        # Times past midnight are written as 24:xx and up, so zero-pad to
        # compare them as strings.
        deps = sorted((t[1] for t in trips), key=lambda d: d.zfill(8))
        rows.append({
            "agency": key[0], "line": key[1], "type": key[2], **typical,
            "first_departure": deps[0], "last_departure": deps[-1],
            "stops": len({parent.get(s) or s for t in trips for s in t[2]}),
        })
    return rows, window


def read_summary(path):
    try:
        with open(path, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []


def write_summary(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, SUMMARY_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def commit_message(old_rows, new_rows):
    def index(rows):
        return {(r["agency"], r["line"], r["type"]):
                [str(r[f]) for f in SUMMARY_FIELDS] for r in rows}

    def describe(keys, verb):
        if not keys:
            return []
        if len(keys) <= 3:
            names = ", ".join(f"{t} {line}" for _, line, t in sorted(keys))
            return [f"{verb} {names}"]
        return [f"{verb} {len(keys)} lines"]

    old, new = index(old_rows), index(new_rows)
    changed = sum(1 for k in old.keys() & new.keys() if old[k] != new[k])
    parts = (describe(new.keys() - old.keys(), "added")
             + describe(old.keys() - new.keys(), "removed"))
    if changed:
        parts.append(f"{changed} lines changed")
    return f"Update GTFS summary: {', '.join(parts) or 'no changes'} [automated]"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--feed", help="use this feed zip instead of "
                        "downloading " + FEED_URL)
    parser.add_argument("--zip", required=True, help="output GTFS subset")
    parser.add_argument("--summary", default="data/gtfs/lines.csv")
    parser.add_argument("--stations", default="data/stations.json")
    parser.add_argument("--commit-message", help="write a commit message "
                        "describing the summary changes to this file")
    parser.add_argument("--release-notes", help="write release notes to "
                        "this file")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        feed = args.feed
        if not feed:
            feed = Path(tmp) / "feed.zip"
            download(FEED_URL, feed)
        subset = build_subset(feed, args.zip, station_bbox(args.stations))

    rows, window = summarize(subset)
    log(f"Feed window {window[0]} to {window[1]}, {len(rows)} lines")

    if args.commit_message:
        Path(args.commit_message).write_text(
            commit_message(read_summary(args.summary), rows) + "\n")
    write_summary(args.summary, rows)

    if args.release_notes:
        Path(args.release_notes).write_text(
            f"VVO-area subset of the gtfs.de local transit feed ({FEED_URL}).\n\n"
            f"Service dates: {window[0]} to {window[1]}.\n\n"
            "Data by DELFI e.V. and OpenStreetMap contributors, "
            "redistributed by gtfs.de under a Creative Commons 4.0 license. "
            "See attributions.txt and feed_info.txt.\n")


if __name__ == "__main__":
    main()
