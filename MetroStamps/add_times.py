#!/usr/bin/env python
# encoding: utf-8
"""
add_times.py — interactive timing data entry for Taipei MRT path finder.

Usage:
  python add_times.py                       # enter/update timing data interactively
  python add_times.py --validate            # check times.csv for completeness
  python add_times.py --reset               # regenerate times.csv template
  python add_times.py --generate-timetable  # create timetable.csv with defaults
"""

import argparse
import csv
import os
import sys

from LineStations import LINE_NODES
import config

TIMES_CSV = os.path.join(os.path.dirname(__file__), 'times.csv')
FIELDNAMES = ['type', 'line', 'from_station', 'to_station', 'minutes']

from metro_graph import load_times
from schedule import (generate_timetable_csv, generate_departures_csv,
                      TIMETABLE_CSV, DEPARTURES_CSV)


# ---------------------------------------------------------------------------
# Build the canonical set of rows from topology
# ---------------------------------------------------------------------------

def _all_edge_rows():
    """All adjacent station pairs across all lines."""
    rows = []
    for line, stations in LINE_NODES.items():
        for i in range(len(stations) - 1):
            rows.append({
                'type': 'edge',
                'line': line,
                'from_station': stations[i],
                'to_station': stations[i + 1],
                'minutes': config.DEFAULT_EDGE_TIME,
            })
    return rows


def _all_transfer_rows():
    """All unique pairs of lines sharing a station name."""
    from collections import defaultdict
    station_lines = defaultdict(list)
    for line, stations in LINE_NODES.items():
        for stn in stations:
            station_lines[stn].append(line)

    rows = []
    for stn, lines in sorted(station_lines.items()):
        if len(lines) < 2:
            continue
        for i, la in enumerate(lines):
            for lb in lines[i + 1:]:
                # Check for special-cased transfer times
                special = config.SPECIAL_TRANSFER_TIMES.get((stn, la, lb),
                          config.SPECIAL_TRANSFER_TIMES.get((stn, lb, la),
                          config.DEFAULT_TRANSFER_TIME))
                rows.append({
                    'type': 'transfer',
                    'line': '',
                    'from_station': stn,
                    'to_station': f'{la}→{lb}',
                    'minutes': special,
                })
    return rows


def canonical_rows():
    return _all_edge_rows() + _all_transfer_rows()


# ---------------------------------------------------------------------------
# CSV read / write
# ---------------------------------------------------------------------------

def load_csv(path):
    """Return list of row dicts. Empty list if file doesn't exist."""
    if not os.path.exists(path):
        return []
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def save_csv(path, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _row_key(row):
    """Unique key for a row regardless of direction."""
    if row['type'] == 'edge':
        a, b = row['from_station'], row['to_station']
        return ('edge', row['line'], min(a, b), max(a, b))
    else:
        return ('transfer', row['from_station'], row['to_station'])


# ---------------------------------------------------------------------------
# Generate / merge template
# ---------------------------------------------------------------------------

def generate_template(path, force=False):
    """Create times.csv with all canonical rows at default values."""
    if os.path.exists(path) and not force:
        print(f"times.csv already exists at {path}")
        print("Use --reset to overwrite, or run without flags to enter data interactively.")
        return False

    rows = canonical_rows()
    save_csv(path, rows)
    print(f"Generated {len(rows)} rows ({len(_all_edge_rows())} edges, "
          f"{len(_all_transfer_rows())} transfers) → {path}")
    return True


# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------

def validate(path):
    existing = load_csv(path)
    existing_keys = {_row_key(r) for r in existing}
    canon = canonical_rows()
    canon_keys = {_row_key(r) for r in canon}

    errors = []
    for row in canon:
        if _row_key(row) not in existing_keys:
            label = (f"{row['line']}: {row['from_station']}→{row['to_station']}"
                     if row['type'] == 'edge'
                     else f"transfer {row['from_station']} ({row['to_station']})")
            errors.append(f"  MISSING: {label}")

    for row in existing:
        try:
            float(row['minutes'])
        except (ValueError, KeyError):
            errors.append(f"  BAD VALUE: {row}")

    if errors:
        print(f"Validation failed — {len(errors)} issue(s):")
        for e in errors:
            print(e)
        return False

    defaults = [r for r in existing
                if float(r['minutes']) == config.DEFAULT_EDGE_TIME and r['type'] == 'edge'
                or float(r['minutes']) == config.DEFAULT_TRANSFER_TIME and r['type'] == 'transfer']
    print(f"OK — {len(existing)} rows, {len(defaults)} still at default value.")
    return True


# ---------------------------------------------------------------------------
# Interactive session
# ---------------------------------------------------------------------------

def _describe_row(row, idx, total):
    if row['type'] == 'edge':
        return (f"[{idx}/{total}] Line {row['line']}: "
                f"{row['from_station']} → {row['to_station']}")
    else:
        return (f"[{idx}/{total}] Transfer at {row['from_station']}: "
                f"{row['to_station']}")


def interactive(path):
    # Ensure the file exists first
    if not os.path.exists(path):
        print("No times.csv found — generating template first...")
        generate_template(path)

    rows = load_csv(path)
    existing_map = {_row_key(r): r for r in rows}

    # Only prompt for entries still at their default value
    canon = canonical_rows()
    to_fill = []
    for row in canon:
        key = _row_key(row)
        current = existing_map.get(key, row)
        cur_val = float(current['minutes'])
        default = (config.DEFAULT_EDGE_TIME if row['type'] == 'edge'
                   else config.DEFAULT_TRANSFER_TIME)
        if cur_val == default:
            to_fill.append((key, current))

    if not to_fill:
        print("All entries already have real values. Nothing to fill in.")
        print("Edit times.csv directly to change any value, then run --validate.")
        return

    print(f"\n{len(to_fill)} entries still at default value.")
    print("Press Enter to keep the current value, or type a new number.")
    print("Ctrl+C to stop and save progress.\n")

    changed = 0
    try:
        for i, (key, row) in enumerate(to_fill, 1):
            default = (config.DEFAULT_EDGE_TIME if row['type'] == 'edge'
                       else config.DEFAULT_TRANSFER_TIME)
            desc = _describe_row(row, i, len(to_fill))
            print(desc)
            print(f"  Current value: {row['minutes']} (default={default})")
            raw = input("  Enter minutes (or Enter to keep): ").strip()

            if raw == '':
                continue

            try:
                val = float(raw)
                if val <= 0:
                    print("  Must be positive — keeping current value.")
                    continue
            except ValueError:
                print("  Not a valid number — keeping current value.")
                continue

            row['minutes'] = val
            existing_map[key] = row
            changed += 1

            # Save after every change
            merged = list(existing_map.values())
            save_csv(path, merged)

    except KeyboardInterrupt:
        print(f"\n\nStopped. {changed} value(s) saved to {path}.")
        return

    print(f"\nDone. {changed} value(s) updated. Saved to {path}.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Taipei MRT timing data entry')
    parser.add_argument('--validate', action='store_true',
                        help='Check times.csv for completeness')
    parser.add_argument('--reset', action='store_true',
                        help='Regenerate times.csv template (overwrites existing)')
    parser.add_argument('--generate-timetable', action='store_true',
                        help='Create timetable.csv with pre-populated default values')
    parser.add_argument('--generate-departures', action='store_true',
                        help='Expand timetable.csv into explicit per-station departures.csv')
    args = parser.parse_args()

    if args.reset:
        ans = input(f"This will overwrite {TIMES_CSV}. Continue? [y/N] ").strip().lower()
        if ans == 'y':
            generate_template(TIMES_CSV, force=True)
        else:
            print("Aborted.")
    elif args.validate:
        ok = validate(TIMES_CSV)
        sys.exit(0 if ok else 1)
    elif args.generate_timetable:
        generate_timetable_csv(TIMETABLE_CSV)
    elif args.generate_departures:
        et = load_times(TIMES_CSV)
        generate_departures_csv(DEPARTURES_CSV, TIMETABLE_CSV, et)
    else:
        interactive(TIMES_CSV)


if __name__ == '__main__':
    main()
