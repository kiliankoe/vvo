#!/usr/bin/env python3

"""Generate descriptive commit messages for automated station data updates.

Compares old and new data files to produce a commit message summarizing
what actually changed, instead of a generic "Update station data" message.

Usage:
    python generate_commit_message.py <old_summary> <new_summary> <old_csv> <new_csv>

All arguments are file paths. Pass /dev/null for missing files (e.g. first commit).
Outputs the commit message to stdout.
"""

import re
import sys


def parse_summary(text):
    """Parse stations_summary.md into structured data."""
    result = {
        "total": 0,
        "transit_types": {},
        "operators": {},
        "hubs": {},
    }

    if not text.strip():
        return result

    # Total stations
    m = re.search(r"Total stations:\s*(\d+)", text)
    if m:
        result["total"] = int(m.group(1))

    # Stations by Transit Type: "- Regionalbus: 2708 stations"
    in_section = None
    for line in text.splitlines():
        line = line.strip()

        if line.startswith("## "):
            if "Transit Type" in line:
                in_section = "transit"
            elif "Transit Operators" in line:
                in_section = "operators"
            elif "Major Transit Hubs" in line:
                in_section = "hubs"
            elif "Stations by City" in line:
                in_section = "cities"
            else:
                in_section = None
            continue

        if not line.startswith("- "):
            continue

        if in_section == "transit":
            m = re.match(r"- (.+?):\s*(\d+)\s*stations", line)
            if m:
                result["transit_types"][m.group(1)] = int(m.group(2))
        elif in_section == "operators":
            m = re.match(r"- (.+?):\s*(\d+)\s*stations", line)
            if m:
                result["operators"][m.group(1)] = int(m.group(2))
        elif in_section == "hubs":
            m = re.match(r"- (.+?):\s*(\d+)\s*lines", line)
            if m:
                result["hubs"][m.group(1)] = int(m.group(2))

    return result


def parse_csv_ids(text):
    """Extract station IDs and name_with_city from CSV."""
    stations = {}
    for line in text.splitlines()[1:]:  # skip header
        if not line.strip():
            continue
        parts = line.split(",")
        if len(parts) >= 5:
            station_id = parts[0]
            name_with_city = parts[4]
            stations[station_id] = name_with_city
    return stations


def format_delta(old_val, new_val):
    """Format a numeric change."""
    diff = new_val - old_val
    if diff > 0:
        return f"+{diff}"
    return str(diff)


def generate_message(old_summary_text, new_summary_text, old_csv_text, new_csv_text):
    """Generate a descriptive commit message from old vs new data."""
    old = parse_summary(old_summary_text)
    new = parse_summary(new_summary_text)

    parts = []

    # 1. Station count changes + identify added/removed stations
    if old["total"] != new["total"]:
        old_ids = parse_csv_ids(old_csv_text)
        new_ids = parse_csv_ids(new_csv_text)
        added = sorted(new_ids[sid] for sid in set(new_ids) - set(old_ids))
        removed = sorted(old_ids[sid] for sid in set(old_ids) - set(new_ids))

        max_names = 3
        names = []
        for name in removed[:max_names]:
            names.append(f"removed {name}")
        for name in added[:max_names - len(names)]:
            names.append(f"added {name}")
        extra = len(added) + len(removed) - len(names)

        if names:
            label = ", ".join(names)
            if extra > 0:
                label += f" +{extra} more"
            parts.append(f"{label} ({old['total']}\u2192{new['total']})")
        else:
            parts.append(f"{old['total']}\u2192{new['total']} stations")

    # 2. Transit type changes
    transit_changes = []
    all_types = set(old["transit_types"].keys()) | set(new["transit_types"].keys())
    for t in sorted(all_types):
        old_val = old["transit_types"].get(t, 0)
        new_val = new["transit_types"].get(t, 0)
        if old_val != new_val:
            transit_changes.append((t, old_val, new_val))

    # 3. Operator changes
    operator_changes = []
    all_ops = set(old["operators"].keys()) | set(new["operators"].keys())
    for op in sorted(all_ops):
        old_val = old["operators"].get(op, 0)
        new_val = new["operators"].get(op, 0)
        if old_val != new_val:
            operator_changes.append((op, old_val, new_val))

    # 4. Hub line count changes (only real changes, not just reordering)
    hub_changes = []
    all_hubs = set(old["hubs"].keys()) | set(new["hubs"].keys())
    for hub in all_hubs:
        old_val = old["hubs"].get(hub, 0)
        new_val = new["hubs"].get(hub, 0)
        if old_val != new_val:
            hub_changes.append((hub, old_val, new_val))
    # Sort by absolute change descending, then by new value descending
    hub_changes.sort(key=lambda x: (-abs(x[2] - x[1]), -x[2]))

    # Build message from changes, keeping it concise
    # Add transit type changes (most interesting category)
    if transit_changes:
        # Sort by absolute change descending
        transit_changes.sort(key=lambda x: -abs(x[2] - x[1]))
        for name, old_val, new_val in transit_changes[:2]:
            parts.append(f"{name} {old_val}\u2192{new_val}")

    # Add operator changes if we have room
    if operator_changes and len(parts) < 3:
        operator_changes.sort(key=lambda x: -abs(x[2] - x[1]))
        for name, old_val, new_val in operator_changes[:2 if not parts else 1]:
            parts.append(f"{name} {old_val}\u2192{new_val}")

    # Add hub changes if we have room
    if hub_changes and len(parts) < 3:
        # Shorten hub names for the commit message
        for name, old_val, new_val in hub_changes[:2 if not parts else 1]:
            short_name = shorten_hub_name(name)
            parts.append(f"{short_name} {old_val}\u2192{new_val} lines")

    # If summary didn't change at all, check CSV for coordinate-only changes
    if not parts:
        if old_csv_text != new_csv_text:
            parts.append("coordinate corrections")
        else:
            parts.append("minor changes")

    title = "Update station data: " + ", ".join(parts) + " [automated]"
    return title


def shorten_hub_name(name):
    """Shorten a hub name for commit messages."""
    # Remove city prefix for Dresden (most common)
    name = re.sub(r"^Dresden ", "", name)
    # Common abbreviations
    name = name.replace("Hauptbahnhof", "Hbf")
    name = name.replace("Bahnhof", "Bf")
    name = name.replace("Busbahnhof", "Busbf")
    return name


def main():
    if len(sys.argv) != 5:
        print(
            f"Usage: {sys.argv[0]} <old_summary> <new_summary> <old_csv> <new_csv>",
            file=sys.stderr,
        )
        sys.exit(1)

    old_summary_path, new_summary_path, old_csv_path, new_csv_path = sys.argv[1:5]

    def read_file(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except (FileNotFoundError, IsADirectoryError):
            return ""

    old_summary = read_file(old_summary_path)
    new_summary = read_file(new_summary_path)
    old_csv = read_file(old_csv_path)
    new_csv = read_file(new_csv_path)

    message = generate_message(old_summary, new_summary, old_csv, new_csv)
    print(message)


if __name__ == "__main__":
    main()
