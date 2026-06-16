#!/usr/bin/env python
# encoding: utf-8
"""
schedule.py — timetable loading and wait-time computation.

Timetable CSV format:
  line, from_terminal, frequency_minutes, first_departure, last_departure

A row like:
  淡水信義線, 淡水, 6, 06:00, 23:59
means trains depart 淡水 heading toward 象山 every 6 min, first at 06:00,
last at 23:59.  The departure time from any intermediate station S is:
  first_departure_from_terminal + cumulative_travel_time(terminal → S)

All times are stored as float minutes since midnight (06:00 = 360.0).
"""

import csv
import os
from typing import Dict, List, Optional, Tuple

from LineStations import LINE_NODES
import config

TIMETABLE_CSV = os.path.join(os.path.dirname(__file__), 'timetable.csv')
TIMETABLE_FIELDS = ['line', 'from_terminal', 'frequency_minutes',
                    'first_departure', 'last_departure']

DEPARTURES_CSV = os.path.join(os.path.dirname(__file__), 'departures.csv')
DEPARTURES_FIELDS = ['line', 'station', 'toward_terminal', 'departure_time']


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

def parse_time(s: str) -> float:
    """'HH:MM' → minutes since midnight."""
    h, m = s.strip().split(':')
    return int(h) * 60 + int(m)


def format_time(minutes: float) -> str:
    """Minutes since midnight → 'HH:MM'."""
    if minutes != minutes:  # NaN
        return '??:??'
    if not (minutes < float('inf')):  # inf
        return '--:--'
    total = int(round(minutes))
    return f"{total // 60:02d}:{total % 60:02d}"


# ---------------------------------------------------------------------------
# Timetable type
# ---------------------------------------------------------------------------

# Key: (line, from_terminal)
# Value: (frequency_min, first_min, last_min)  — all in minutes since midnight
Timetable = Dict[Tuple[str, str], Tuple[float, float, float]]


def load_timetable(path: str) -> Timetable:
    timetable: Timetable = {}
    if not os.path.exists(path):
        return timetable
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            key = (row['line'].strip(), row['from_terminal'].strip())
            timetable[key] = (
                float(row['frequency_minutes']),
                parse_time(row['first_departure']),
                parse_time(row['last_departure']),
            )
    return timetable


# ---------------------------------------------------------------------------
# Departures type — explicit per-station timetables
# ---------------------------------------------------------------------------

# Key: (line, station, toward_terminal)
# Value: sorted list of departure times (minutes since midnight)
Departures = Dict[Tuple[str, str, str], List[float]]


def load_departures(path: str) -> Departures:
    """Load departures.csv into a Departures dict. Returns empty dict if absent."""
    departures: Departures = {}
    if not os.path.exists(path):
        return departures
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            key = (row['line'].strip(), row['station'].strip(),
                   row['toward_terminal'].strip())
            departures.setdefault(key, []).append(parse_time(row['departure_time']))
    for key in departures:
        departures[key].sort()
    return departures


def generate_departures_csv(path: str, timetable_path: str, et,
                             force: bool = False) -> bool:
    """Expand timetable.csv into an explicit per-station departures.csv."""
    if os.path.exists(path) and not force:
        print(f"departures.csv already exists at {path}")
        print("Use --reset to overwrite.")
        return False

    timetable = load_timetable(timetable_path)
    rows = []
    for (line, from_terminal), (freq, first, last) in sorted(timetable.items()):
        stations = LINE_NODES[line]
        toward_terminal = (stations[-1] if stations[0] == from_terminal
                           else stations[0])
        try:
            offsets = cumulative_offsets(line, from_terminal, et)
        except ValueError:
            continue
        for stn in stations:
            offset = offsets.get(stn, 0.0)
            t = first + offset
            last_at = last + offset
            while t <= last_at + 1e-9:
                rows.append({
                    'line': line,
                    'station': stn,
                    'toward_terminal': toward_terminal,
                    'departure_time': format_time(t),
                })
                t += freq

    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=DEPARTURES_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} departure rows → {path}")
    return True


# ---------------------------------------------------------------------------
# Station offsets (cumulative travel time along a line)
# ---------------------------------------------------------------------------

def _edge_times_for_line(line: str, et) -> List[float]:
    """List of travel times for each adjacent pair on line (from station 0 onward)."""
    from metro_graph import _edge_time
    stations = LINE_NODES[line]
    return [_edge_time(et, stations[i], stations[i + 1], line)
            for i in range(len(stations) - 1)]


def cumulative_offsets(line: str, from_terminal: str, et) -> Dict[str, float]:
    """
    Returns {station: minutes_from_terminal} for all stations on line,
    measured in the direction from from_terminal toward the other terminal.
    """
    stations = LINE_NODES[line]
    if stations[0] == from_terminal:
        ordered = stations
    elif stations[-1] == from_terminal:
        ordered = list(reversed(stations))
    else:
        raise ValueError(f"{from_terminal} is not a terminal of {line}")

    offsets: Dict[str, float] = {}
    cum = 0.0
    for i, stn in enumerate(ordered):
        offsets[stn] = cum
        if i < len(ordered) - 1:
            from metro_graph import _edge_time
            cum += _edge_time(et, ordered[i], ordered[i + 1], line)
    return offsets


# ---------------------------------------------------------------------------
# Wait computation
# ---------------------------------------------------------------------------

def next_departure(station: str, line: str, toward_terminal: str,
                   after_time: float,
                   timetable: Timetable, et,
                   departures: 'Departures | None' = None) -> float:
    """
    Returns the next departure time (minutes since midnight) of a train at
    `station` on `line` heading toward `toward_terminal`, not earlier than
    `after_time`.

    Checks departures.csv entries first; falls back to frequency-based timetable.
    Returns float('inf') if no more trains are available today.
    """
    # Check explicit per-station departures first
    if departures:
        key = (line, station, toward_terminal)
        if key in departures:
            for t in departures[key]:
                if t >= after_time - 1e-9:
                    return t
            return float('inf')

    stations = LINE_NODES[line]

    # The train comes FROM the opposite terminal
    if stations[0] == toward_terminal:
        from_terminal = stations[-1]
    elif stations[-1] == toward_terminal:
        from_terminal = stations[0]
    else:
        raise ValueError(f"{toward_terminal} is not a terminal of {line}")

    key = (line, from_terminal)
    if key not in timetable:
        # No timetable entry: fall back to "always available" (0 wait)
        return after_time

    freq, first_from_terminal, last_from_terminal = timetable[key]

    # Offset of station from from_terminal (in the direction toward toward_terminal)
    offsets = cumulative_offsets(line, from_terminal, et)
    offset = offsets.get(station, 0.0)

    first_at_station = first_from_terminal + offset
    last_at_station = last_from_terminal + offset

    if after_time > last_at_station:
        return float('inf')  # missed the last train

    if after_time <= first_at_station:
        return first_at_station

    # How many full periods have elapsed since first_at_station?
    k = int((after_time - first_at_station) / freq)
    candidate = first_at_station + k * freq
    if candidate < after_time - 1e-9:
        candidate += freq
    return min(candidate, last_at_station + freq)  # don't go past last


# ---------------------------------------------------------------------------
# Timetable-aware simulation
# ---------------------------------------------------------------------------

def determine_direction(u_station: str, v_station: str, line: str) -> str:
    """Return the toward_terminal for a u→v step on line."""
    stations = LINE_NODES[line]
    idx_u = stations.index(u_station)
    idx_v = stations.index(v_station)
    return stations[-1] if idx_v > idx_u else stations[0]


# A simulated step with timing info
SimStep = Tuple  # (u_node, v_node, travel_time, label,
                 #  wait_before, depart_time, arrive_time)


def simulate(steps: List, start_time: float,
             timetable: Timetable, et,
             departures: 'Departures | None' = None) -> List[SimStep]:
    """
    Takes the output of expand_walk and augments each step with:
      wait_before: minutes waiting at station before this step
      depart_time: wall-clock time the train departs (= arrive_prev + wait)
      arrive_time: wall-clock time at destination

    Transfer steps (same station, different line) record the platform-walk
    time and the wait for the new line.
    """
    current_time = start_time
    on_line: Optional[str] = None       # line I'm currently riding
    on_toward: Optional[str] = None     # toward_terminal of current ride
    result: List[SimStep] = []

    for i, (u, v, w, lbl) in enumerate(steps):
        u_stn, u_line = u
        v_stn, v_line = v

        if lbl == 'walk':
            # ── Above-ground walk (different station, different line) ─────────
            on_line = None
            on_toward = None
            arrive = current_time + w
            result.append((u, v, w, 'walk', 0.0, current_time, arrive))
            current_time = arrive

        elif lbl == 'transfer':
            # ── Platform walk (u_stn == v_stn, different lines) ──────────────
            # Step off old train
            on_line = None
            on_toward = None

            # Walk to new platform
            walk_time = w
            current_time += walk_time

            # Is this a same-train through-service? (e.g., 大橋頭 B→A)
            same_train = (u_stn, u_line, v_line) in config.SAME_TRAIN_TRANSFERS or \
                         (u_stn, v_line, u_line) in config.SAME_TRAIN_TRANSFERS

            if same_train:
                # No boarding wait — train continues directly
                wait = 0.0
                on_line = v_line
                # Determine direction from next non-transfer step
                on_toward = _lookahead_direction(steps, i + 1, v_line)
            else:
                # Wait for next train on new line
                toward = _lookahead_direction(steps, i + 1, v_line)
                dep = next_departure(v_stn, v_line, toward, current_time,
                                     timetable, et, departures)
                wait = dep - current_time
                current_time = dep
                on_line = v_line
                on_toward = toward

            result.append((u, v, walk_time, 'transfer', wait,
                           current_time - wait, current_time))

        else:
            # ── Travel step ──────────────────────────────────────────────────
            # Do we need to board a new train?
            need_board = (on_line is None or on_line != v_line)

            if need_board:
                toward = determine_direction(u_stn, v_stn, v_line)
                dep = next_departure(u_stn, v_line, toward, current_time,
                                     timetable, et, departures)
                wait = dep - current_time
                current_time = dep
                on_line = v_line
                on_toward = toward
            else:
                wait = 0.0

            arrive = current_time + w
            result.append((u, v, w, lbl, wait, current_time, arrive))
            current_time = arrive

    return result


def _lookahead_direction(steps: List, from_idx: int, line: str) -> Optional[str]:
    """Scan ahead to find the first regular step on `line` and return its direction."""
    for j in range(from_idx, len(steps)):
        u2, v2, _, lbl2 = steps[j]
        if lbl2 != 'transfer' and u2[1] == line and v2[1] == line:
            return determine_direction(u2[0], v2[0], line)
    # Fallback: use last station of line as direction
    return LINE_NODES[line][-1]


# ---------------------------------------------------------------------------
# Timetable CSV generation
# ---------------------------------------------------------------------------

def generate_timetable_csv(path: str, force: bool = False) -> bool:
    if os.path.exists(path) and not force:
        print(f"timetable.csv already exists at {path}")
        print("Use --reset to overwrite.")
        return False

    rows = []
    for line, stations in LINE_NODES.items():
        freq = config.BRANCH_LINE_FREQUENCY.get(line, config.DEFAULT_FREQUENCY)
        for terminal in (stations[0], stations[-1]):
            rows.append({
                'line': line,
                'from_terminal': terminal,
                'frequency_minutes': freq,
                'first_departure': config.DEFAULT_FIRST_TRAIN,
                'last_departure': config.DEFAULT_LAST_TRAIN,
            })

    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=TIMETABLE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} timetable rows → {path}")
    return True
