#!/usr/bin/env python
# encoding: utf-8
"""
find_path.py — find the fastest path visiting all Taipei MRT stations.

Modes:
  fastest  — minimise total travel + transfer cost (no timetable, default if
             timetable.csv is absent)
  earliest — given a real start time, simulate actual wait times using
             timetable.csv and report wall-clock finish time

Usage:
  python find_path.py
  python find_path.py --start 象山 --start-time 06:00
  python find_path.py --start 台北車站 --mode fastest --top 3
  python find_path.py --start 象山 --mode earliest --start-time 08:30
"""

import argparse
import os
import random
import sys
from typing import Dict, List, Optional, Tuple

from LineStations import LINE_NODES
import config
from metro_graph import (
    Node, EdgeTimings, Graph, MacroGraph, MacroEdge,
    get_station_lines,
    load_times, load_walks, build_graph, compute_apsp, reconstruct_path,
    build_macro_graph, compute_macro_apsp, reconstruct_macro_path,
    WALKS_CSV,
)
from schedule import (
    load_timetable, load_departures, simulate,
    format_time, parse_time, TIMETABLE_CSV, DEPARTURES_CSV,
)

TIMES_CSV = os.path.join(os.path.dirname(__file__), 'times.csv')


# ---------------------------------------------------------------------------
# Segment-coverage walk
#
# Every macro-edge must be physically traversed at least once, because each
# has unique interior stations (or is the only way to reach an endpoint).
# We greedily find the nearest untraversed segment, travel to its nearer
# endpoint, traverse it, repeat.  Then apply 2-opt on the segment order.
# ---------------------------------------------------------------------------

def _segment_cost(start: str, seg: MacroEdge,
                  macro_apsp: Dict[Tuple[str, str], float]) -> Tuple[float, str, str]:
    """Return (total_cost, entry_key, exit_key) to traverse seg from start."""
    cost_fwd = macro_apsp.get((start, seg.from_key), float('inf')) + seg.weight
    cost_bwd = macro_apsp.get((start, seg.to_key), float('inf')) + seg.weight
    if cost_fwd <= cost_bwd:
        return cost_fwd, seg.from_key, seg.to_key
    else:
        return cost_bwd, seg.to_key, seg.from_key


def greedy_segment_walk(start_key: str, macro_graph: MacroGraph,
                         macro_apsp: Dict[Tuple[str, str], float],
                         all_macro_prev: Dict[str, Dict[str, Optional[str]]],
                         randomize: bool = False
                         ) -> List[Tuple[str, str, Optional[int]]]:
    """
    Returns a walk as list of (from_key, to_key, seg_idx_or_None).
    seg_idx is the index into macro_graph.macro_edges; None means transit.
    """
    segs = macro_graph.macro_edges
    unvisited = set(range(len(segs)))
    walk: List[Tuple[str, str, Optional[int]]] = []
    current = start_key

    while unvisited:
        # Find nearest untraversed segment (with optional randomization)
        candidates = list(unvisited)
        if randomize and len(candidates) > 1:
            random.shuffle(candidates)
            # Pick from top-3 by cost to introduce diversity
            scored = sorted(candidates,
                            key=lambda i: _segment_cost(current, segs[i], macro_apsp)[0])
            pool = scored[:max(3, len(scored) // 4)]
            chosen_i = random.choice(pool)
        else:
            chosen_i = min(candidates,
                           key=lambda i: _segment_cost(current, segs[i], macro_apsp)[0])

        _, entry, exit_key = _segment_cost(current, segs[chosen_i], macro_apsp)

        # Transit to entry (may pass through intermediate key stations)
        if current != entry:
            transit = reconstruct_macro_path(all_macro_prev, current, entry)
            for j in range(len(transit) - 1):
                walk.append((transit[j], transit[j + 1], None))

        # Traverse the segment
        walk.append((entry, exit_key, chosen_i))
        unvisited.discard(chosen_i)
        current = exit_key

    return walk


def walk_total_cost(walk: List[Tuple[str, str, Optional[int]]],
                    macro_graph: MacroGraph,
                    macro_apsp: Dict[Tuple[str, str], float]) -> float:
    total = 0.0
    for from_k, to_k, seg_idx in walk:
        if seg_idx is not None:
            total += macro_graph.macro_edges[seg_idx].weight
        else:
            total += macro_apsp.get((from_k, to_k), float('inf'))
    return total


def _seq_cost(seg_order: List[int], start_key: str, macro_graph: MacroGraph,
               macro_apsp: Dict[Tuple[str, str], float]) -> float:
    """Fast cost estimate for an ordered list of segment indices."""
    total = 0.0
    current = start_key
    for seg_idx in seg_order:
        seg = macro_graph.macro_edges[seg_idx]
        cost_fwd = macro_apsp.get((current, seg.from_key), float('inf')) + seg.weight
        cost_bwd = macro_apsp.get((current, seg.to_key), float('inf')) + seg.weight
        if cost_fwd <= cost_bwd:
            total += cost_fwd
            current = seg.to_key
        else:
            total += cost_bwd
            current = seg.from_key
    return total


def _rebuild_walk(seg_order: List[int], start_key: str, macro_graph: MacroGraph,
                   macro_apsp: Dict[Tuple[str, str], float],
                   all_macro_prev: Dict[str, Dict[str, Optional[str]]]
                   ) -> List[Tuple[str, str, Optional[int]]]:
    new_walk = []
    cur = start_key
    for seg_idx in seg_order:
        seg = macro_graph.macro_edges[seg_idx]
        _, entry, exit_k = _segment_cost(cur, seg, macro_apsp)
        if cur != entry:
            transit = reconstruct_macro_path(all_macro_prev, cur, entry)
            for j in range(len(transit) - 1):
                new_walk.append((transit[j], transit[j + 1], None))
        new_walk.append((entry, exit_k, seg_idx))
        cur = exit_k
    return new_walk


def two_opt_segments(walk: List[Tuple[str, str, Optional[int]]],
                     macro_graph: MacroGraph,
                     macro_apsp: Dict[Tuple[str, str], float],
                     all_macro_prev: Dict[str, Dict[str, Optional[str]]],
                     start_key: str) -> List[Tuple[str, str, Optional[int]]]:
    """2-opt improvement on segment traversal order."""
    best_order = [seg_idx for _, _, seg_idx in walk if seg_idx is not None]
    best_cost = _seq_cost(best_order, start_key, macro_graph, macro_apsp)

    improved = True
    while improved:
        improved = False
        for i in range(len(best_order) - 1):
            for j in range(i + 1, len(best_order)):
                candidate = best_order[:i] + list(reversed(best_order[i:j + 1])) + best_order[j + 1:]
                c = _seq_cost(candidate, start_key, macro_graph, macro_apsp)
                if c < best_cost - 1e-9:
                    best_order = candidate
                    best_cost = c
                    improved = True

    return _rebuild_walk(best_order, start_key, macro_graph, macro_apsp, all_macro_prev)


def find_n_best_walks(start_key: str, macro_graph: MacroGraph,
                       macro_apsp: Dict[Tuple[str, str], float],
                       all_macro_prev: Dict[str, Dict[str, Optional[str]]],
                       n: int, random_starts: int
                       ) -> List[List[Tuple[str, str, Optional[int]]]]:
    seen = set()
    results = []

    def try_add(w):
        key = tuple(w)
        if key not in seen:
            seen.add(key)
            results.append(w)

    # Deterministic first pass
    w = greedy_segment_walk(start_key, macro_graph, macro_apsp, all_macro_prev,
                             randomize=False)
    w = two_opt_segments(w, macro_graph, macro_apsp, all_macro_prev, start_key)
    try_add(w)

    # Random restarts
    for _ in range(random_starts):
        w = greedy_segment_walk(start_key, macro_graph, macro_apsp, all_macro_prev,
                                 randomize=True)
        w = two_opt_segments(w, macro_graph, macro_apsp, all_macro_prev, start_key)
        try_add(w)

    results.sort(key=lambda w: walk_total_cost(w, macro_graph, macro_apsp))
    return results[:n]


# ---------------------------------------------------------------------------
# Expand walk to full station-by-station itinerary
# ---------------------------------------------------------------------------

Step = Tuple[Node, Node, float, str]  # (from_node, to_node, cost, label)


def expand_walk(walk: List[Tuple[str, str, Optional[int]]],
                start_stn: str,
                macro_graph: MacroGraph,
                graph: Graph,
                all_prev: Dict[Node, Dict[Node, Optional[Node]]],
                all_dist: Dict[Tuple[Node, Node], float],
                et: EdgeTimings) -> List[Step]:
    """
    Expand a macro-walk into individual station steps.
    For segment traversals: physically ride through all interior stations.
    For transit hops: use APSP (may visit bonus stations along the way).
    """
    from metro_graph import _edge_time, _transfer_time

    station_lines = get_station_lines()
    steps: List[Step] = []
    visited_stations: set = set()
    branch_junctions_done: set = set()

    def best_node_for(stn: str, prefer_line: Optional[str] = None) -> Node:
        lines = station_lines[stn]
        if prefer_line and prefer_line in lines:
            return (stn, prefer_line)
        return (stn, lines[0])

    def add_apsp_steps(from_node: Node, to_node: Node, label: str = '') -> Node:
        """Travel from from_node to to_node via APSP, appending steps. Returns final node."""
        if from_node == to_node:
            return from_node
        path = reconstruct_path(all_prev[from_node], from_node, to_node)
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if u[0] == v[0]:  # transfer (same station, different line)
                w = _transfer_time(et, u[0], u[1], v[1])
                steps.append((u, v, w, 'transfer'))
            elif (u[0], u[1], v[0], v[1]) in et.walk_times:  # above-ground walk
                w = et.walk_times[(u[0], u[1], v[0], v[1])]
                steps.append((u, v, w, 'walk'))
            else:  # regular travel
                w = _edge_time(et, u[0], v[0], u[1])
                steps.append((u, v, w, label))
            visited_stations.add(v[0])
        return path[-1] if path else from_node

    def add_segment_steps(entry_key: str, exit_key: str,
                           seg: MacroEdge, current_node: Node) -> Node:
        """
        Physically ride the segment from entry_key to exit_key,
        visiting all interior stations.  Returns the node at exit_key.
        """
        # Determine station sequence for this traversal
        if seg.from_key == entry_key:
            seq = [seg.from_key] + seg.intermediates + [seg.to_key]
        else:
            seq = [seg.to_key] + list(reversed(seg.intermediates)) + [seg.from_key]

        # Find the right line for this segment
        line = seg.line

        # Transfer to the segment's line if needed
        entry_node = (entry_key, line)
        if current_node != entry_node:
            if current_node[0] == entry_key:
                # Same station, different line
                w = _transfer_time(et, entry_key, current_node[1], line)
                steps.append((current_node, entry_node, w, 'transfer'))
                visited_stations.add(entry_key)
                current_node = entry_node
            else:
                current_node = add_apsp_steps(current_node, entry_node)

        # Ride the segment
        for i in range(len(seq) - 1):
            a, b = seq[i], seq[i + 1]
            u, v = (a, line), (b, line)
            w = _edge_time(et, a, b, line)
            steps.append((u, v, w, ''))
            visited_stations.add(b)
            current_node = v

        return current_node

    def add_branch_detour(junction: str, current_node: Node) -> Node:
        """Insert round-trip branch detour from the junction station."""
        interiors = macro_graph.branch_interiors.get(junction, [])
        if not interiors:
            return current_node

        # Find branch line
        first_interior = interiors[0]
        branch_line = None
        for line, stations in LINE_NODES.items():
            if junction in stations and first_interior in stations:
                branch_line = line
                break
        if not branch_line:
            return current_node

        # Transfer to branch line if needed
        junction_node = (junction, branch_line)
        if current_node != junction_node:
            if current_node[0] == junction:
                w = _transfer_time(et, junction, current_node[1], branch_line)
                steps.append((current_node, junction_node, w, 'transfer'))
                current_node = junction_node
            else:
                current_node = add_apsp_steps(current_node, junction_node)

        # Ride to terminus
        full_seq = [junction] + interiors
        for i in range(len(full_seq) - 1):
            a, b = full_seq[i], full_seq[i + 1]
            u, v = (a, branch_line), (b, branch_line)
            w = _edge_time(et, a, b, branch_line)
            steps.append((u, v, w, 'branch'))
            visited_stations.add(b)
            current_node = v

        # Ride back
        for i in range(len(full_seq) - 1, 0, -1):
            a, b = full_seq[i], full_seq[i - 1]
            u, v = (a, branch_line), (b, branch_line)
            w = _edge_time(et, a, b, branch_line)
            steps.append((u, v, w, 'branch'))
            current_node = v

        return current_node

    # --- Start ---
    current_node = best_node_for(start_stn)
    visited_stations.add(start_stn)

    # If start_stn is not the first key station in the walk, travel there first
    if walk:
        first_key = walk[0][0]
        if start_stn != first_key:
            first_node = best_node_for(first_key)
            current_node = add_apsp_steps(current_node, first_node)

    for from_k, to_k, seg_idx in walk:
        # Handle transit leg
        if seg_idx is None:
            to_node = best_node_for(to_k, current_node[1] if current_node[0] == from_k else None)
            current_node = add_apsp_steps(current_node, to_node)
        else:
            # Segment traversal
            seg = macro_graph.macro_edges[seg_idx]
            current_node = add_segment_steps(from_k, to_k, seg, current_node)

        # Insert branch detour when first arriving at a branch junction
        stn = current_node[0]
        if stn in macro_graph.branch_costs and stn not in branch_junctions_done:
            branch_junctions_done.add(stn)
            current_node = add_branch_detour(stn, current_node)

    return steps


# ---------------------------------------------------------------------------
# Output formatting — fastest mode (no timetable)
# ---------------------------------------------------------------------------

def print_path_fastest(steps: List[Step], rank: int, all_stations: set, full_output: bool):
    visited: set = set()
    cumulative = 0.0
    total = sum(w for _, _, w, _ in steps)

    print(f"\n{'=' * 64}")
    print(f"  Path #{rank}  —  Total cost: {total:.1f}")
    print(f"{'=' * 64}")

    for i, (u, v, w, lbl) in enumerate(steps, 1):
        cumulative += w
        from_str = f"{u[0]} ({u[1]})"
        to_str = f"{v[0]} ({v[1]})"

        arrow = ('──[transfer]──>' if lbl == 'transfer'
                 else '~~[walk]~~>' if lbl == 'walk'
                 else '→  [BRANCH]' if lbl == 'branch'
                 else '→')
        tag = ' ★' if (v[0] not in visited and v[0] in all_stations) else ''
        visited.add(u[0])
        visited.add(v[0])

        if full_output:
            print(f"  {i:4d}. {from_str:<32s} {arrow} {to_str}{tag}")
            print(f"         cost: {w:.1f}   cumulative: {cumulative:.1f}")

    _print_coverage(visited, all_stations)


# ---------------------------------------------------------------------------
# Output formatting — earliest mode (with timetable)
# ---------------------------------------------------------------------------

def print_path_earliest(sim_steps: List, rank: int, all_stations: set,
                         start_time: float, full_output: bool):
    """sim_steps: list of (u, v, travel_w, lbl, wait_before, depart, arrive)"""
    visited: set = set()

    end_time = sim_steps[-1][6] if sim_steps else start_time
    elapsed = end_time - start_time
    total_travel = sum(tw for _, _, tw, lbl, _, _, _ in sim_steps
                       if lbl not in ('transfer', 'walk'))
    total_wait = sum(w for _, _, _, _, w, _, _ in sim_steps)

    elapsed_str = f"{elapsed:.0f}" if elapsed == elapsed and elapsed < float('inf') else '??'
    travel_str = f"{total_travel:.0f}" if total_travel == total_travel else '??'
    wait_str_hdr = f"{total_wait:.0f}" if total_wait == total_wait else '??'

    print(f"\n{'=' * 70}")
    print(f"  Path #{rank}  —  Start: {format_time(start_time)}  "
          f"End: {format_time(end_time)}")
    print(f"             {elapsed_str} min total  "
          f"({travel_str} travel + {wait_str_hdr} wait)")
    print(f"{'=' * 70}")

    for i, (u, v, tw, lbl, wait, depart, arrive) in enumerate(sim_steps, 1):
        from_str = f"{u[0]} ({u[1]})"
        to_str = f"{v[0]} ({v[1]})"

        arrow = ('──[transfer]──>' if lbl == 'transfer'
                 else '~~[walk]~~>' if lbl == 'walk'
                 else '→  [BRANCH]' if lbl == 'branch'
                 else '→')
        tag = ' ★' if (v[0] not in visited and v[0] in all_stations) else ''
        visited.add(u[0])
        visited.add(v[0])

        time_str = f"{format_time(depart)}→{format_time(arrive)}"
        wait_str = f" [wait {wait:.0f}m]" if wait == wait and wait > 0 else ""

        if full_output:
            print(f"  {i:4d}. {from_str:<32s} {arrow} {to_str}{tag}")
            print(f"         {time_str:<14s}  travel: {tw:.1f}m{wait_str}")

    _print_coverage(visited, all_stations)


def _print_coverage(visited: set, all_stations: set):
    missed = all_stations - visited
    print(f"\n  Stations visited: {len(visited & all_stations)}/{len(all_stations)}", end='')
    if missed:
        print(f"\n  *** MISSED {len(missed)}: {', '.join(sorted(missed))} ***")
    else:
        print("  ✓")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def resolve_start(start_name: str) -> Optional[str]:
    station_lines = get_station_lines()
    if start_name in station_lines:
        return start_name
    matches = [s for s in station_lines if start_name in s]
    if len(matches) == 1:
        return matches[0]
    if matches:
        print(f"Ambiguous station '{start_name}'. Matches: {matches}")
    else:
        print(f"Station '{start_name}' not found.")
    return None


def nearest_key_station(start_stn: str, macro_graph: MacroGraph,
                          all_dist: Dict[Tuple[Node, Node], float],
                          graph: Graph) -> str:
    """Find the closest key station to start_stn (by full APSP cost)."""
    station_lines = get_station_lines()
    start_node = (start_stn, station_lines[start_stn][0])
    best_key = None
    best_cost = float('inf')
    for ks in macro_graph.key_stations:
        for line in station_lines.get(ks, []):
            c = all_dist.get((start_node, (ks, line)), float('inf'))
            if c < best_cost:
                best_cost = c
                best_key = ks
    return best_key or macro_graph.key_stations[0]


def main():
    parser = argparse.ArgumentParser(
        description='Find fastest path visiting all Taipei MRT stations',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--start', default=config.DEFAULT_START_STATION,
                        help='Starting station name (Chinese)')
    parser.add_argument('--start-time', default=config.DEFAULT_START_TIME,
                        help='Departure time HH:MM (used in earliest mode)')
    parser.add_argument('--mode', choices=['fastest', 'earliest'], default=None,
                        help='fastest: no timetable; earliest: wall-clock simulation '
                             '(auto-selects based on timetable.csv presence)')
    parser.add_argument('--top', type=int, default=config.TOP_N_PATHS,
                        help='Number of paths to show')
    parser.add_argument('--random-starts', type=int, default=config.RANDOM_STARTS,
                        help='Random restarts for greedy walk optimisation')
    parser.add_argument('--times', default=TIMES_CSV,
                        help='Path to times.csv')
    parser.add_argument('--timetable', default=TIMETABLE_CSV,
                        help='Path to timetable.csv')
    parser.add_argument('--departures', default=DEPARTURES_CSV,
                        help='Path to departures.csv (explicit per-station timetable)')
    parser.add_argument('--walks', default=WALKS_CSV,
                        help='Path to walks.csv (above-ground connections)')
    parser.add_argument('--full-output', action='store_true',
                        help='Show every step; omit for summary only')
    args = parser.parse_args()


    # Resolve mode
    timetable = load_timetable(args.timetable)
    if args.mode is None:
        mode = 'earliest' if timetable else 'fastest'
    else:
        mode = args.mode
    if mode == 'earliest' and not timetable:
        print(f"No timetable.csv found at {args.timetable}.")
        print("Run: python add_times.py --generate-timetable")
        print("Falling back to 'fastest' mode.")
        mode = 'fastest'

    start_stn = resolve_start(args.start)
    if start_stn is None:
        sys.exit(1)

    start_time_min = parse_time(args.start_time)

    departures = load_departures(args.departures)

    print(f"Mode: {mode}  |  Start: {start_stn} at {args.start_time}")
    print("Loading graph...")
    et = load_times(args.times)
    load_walks(args.walks, et)
    graph = build_graph(et)
    macro_graph = build_macro_graph(graph, et)

    print("Computing all-pairs shortest paths...")
    all_dist, all_prev = compute_apsp(graph)

    print("Computing macro-graph shortest paths...")
    macro_apsp, all_macro_prev = compute_macro_apsp(macro_graph)

    start_key = (start_stn if start_stn in macro_graph.key_stations
                 else nearest_key_station(start_stn, macro_graph, all_dist, graph))
    print(f"Key station: {start_key}  |  Segments: {len(macro_graph.macro_edges)}")
    print(f"Running greedy walk + 2-opt ({args.random_starts} restarts)...\n")

    walks = find_n_best_walks(start_key, macro_graph, macro_apsp, all_macro_prev,
                               args.top, args.random_starts)

    all_stations = set(get_station_lines().keys())

    full_output = args.full_output

    if mode == 'earliest':
        # Simulate each walk with timetable; re-rank by wall-clock finish time
        simulated = []
        for walk in walks:
            steps = expand_walk(walk, start_stn, macro_graph, graph,
                                all_prev, all_dist, et)
            sim = simulate(steps, start_time_min, timetable, et, departures)
            finish = sim[-1][6] if sim else start_time_min
            simulated.append((finish, steps, sim))
        simulated.sort(key=lambda x: x[0])

        for rank, (finish, steps, sim) in enumerate(simulated, 1):
            print_path_earliest(sim, rank, all_stations, start_time_min, full_output)
    else:
        for rank, walk in enumerate(walks, 1):
            steps = expand_walk(walk, start_stn, macro_graph, graph,
                                all_prev, all_dist, et)
            print_path_fastest(steps, rank, all_stations, full_output)

    print()


if __name__ == '__main__':
    main()
