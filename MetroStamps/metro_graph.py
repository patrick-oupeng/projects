#!/usr/bin/env python
# encoding: utf-8
"""
metro_graph.py — core graph model for Taipei MRT path finder.

Node: (station_name, line_name)
Edges:
  - travel: adjacent stations on the same line
  - transfer: same station name, different lines
"""

import csv
import heapq
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from LineStations import LINE_NODES
import config


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

Node = Tuple[str, str]  # (station, line)


@dataclass
class EdgeTimings:
    # (from_station, to_station, line) -> minutes  (stored as undirected: both orders)
    edge_times: Dict[Tuple[str, str, str], float] = field(default_factory=dict)
    # (station, line_a, line_b) -> minutes  (stored as both orders)
    transfer_times: Dict[Tuple[str, str, str], float] = field(default_factory=dict)
    # (from_station, from_line, to_station, to_line) -> minutes  (above-ground walks)
    walk_times: Dict[Tuple[str, str, str, str], float] = field(default_factory=dict)


@dataclass
class Graph:
    nodes: List[Node]
    # adjacency: node -> list of (neighbour_node, weight)
    adj: Dict[Node, List[Tuple[Node, float]]]


@dataclass
class MacroEdge:
    from_key: str
    to_key: str
    line: str
    weight: float
    intermediates: List[str]  # interior stations in order from_key→to_key


@dataclass
class MacroGraph:
    key_stations: List[str]          # transfer stations + line endpoints
    macro_adj: Dict[str, List[Tuple[str, float]]]  # key_stn -> [(key_stn, cost)]
    macro_edges: List[MacroEdge]
    branch_costs: Dict[str, float]   # junction_stn -> mandatory round-trip cost
    branch_interiors: Dict[str, List[str]]  # junction -> interior stations of branch


# ---------------------------------------------------------------------------
# Identify transfer stations and key stations
# ---------------------------------------------------------------------------

def get_station_lines() -> Dict[str, List[str]]:
    """Return {station_name: [line1, line2, ...]} for all stations."""
    result: Dict[str, List[str]] = {}
    for line, stations in LINE_NODES.items():
        for stn in stations:
            result.setdefault(stn, []).append(line)
    return result


def get_transfer_stations() -> Dict[str, List[str]]:
    """Stations that appear on 2+ lines."""
    return {s: lines for s, lines in get_station_lines().items() if len(lines) > 1}


def get_key_stations() -> List[str]:
    """Transfer stations + line endpoints (first/last of each line)."""
    key = set(get_transfer_stations().keys())
    for stations in LINE_NODES.values():
        key.add(stations[0])
        key.add(stations[-1])
    return sorted(key)


# ---------------------------------------------------------------------------
# Loading timing data
# ---------------------------------------------------------------------------

WALKS_CSV = os.path.join(os.path.dirname(__file__), 'walks.csv')
WALKS_FIELDS = ['from_station', 'from_line', 'to_station', 'to_line', 'walk_minutes', 'notes']


def load_walks(path: str, et: EdgeTimings) -> None:
    """Load walks.csv and add above-ground walking edges to et.walk_times."""
    if not os.path.exists(path):
        return
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            fs = row['from_station'].strip()
            fl = row['from_line'].strip()
            ts = row['to_station'].strip()
            tl = row['to_line'].strip()
            w = float(row['walk_minutes'])
            et.walk_times[(fs, fl, ts, tl)] = w
            et.walk_times[(ts, tl, fs, fl)] = w


def load_times(csv_path: str) -> EdgeTimings:
    """Parse times.csv into EdgeTimings. Falls back to config defaults if absent."""
    et = EdgeTimings()
    if not os.path.exists(csv_path):
        return et  # caller will use defaults via _get_edge_time helpers

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            t = row['type'].strip()
            minutes = float(row['minutes'])
            if t == 'edge':
                line = row['line'].strip()
                a, b = row['from_station'].strip(), row['to_station'].strip()
                et.edge_times[(a, b, line)] = minutes
                et.edge_times[(b, a, line)] = minutes
            elif t == 'transfer':
                stn = row['from_station'].strip()
                # to_station encodes "lineA→lineB"
                parts = row['to_station'].strip().split('→')
                if len(parts) == 2:
                    la, lb = parts[0].strip(), parts[1].strip()
                    et.transfer_times[(stn, la, lb)] = minutes
                    et.transfer_times[(stn, lb, la)] = minutes
    return et


def _edge_time(et: EdgeTimings, a: str, b: str, line: str) -> float:
    return et.edge_times.get((a, b, line), config.DEFAULT_EDGE_TIME)


def _transfer_time(et: EdgeTimings, stn: str, la: str, lb: str) -> float:
    return et.transfer_times.get((stn, la, lb),
           et.transfer_times.get((stn, lb, la), config.DEFAULT_TRANSFER_TIME))


# ---------------------------------------------------------------------------
# Build multi-layer graph
# ---------------------------------------------------------------------------

def build_graph(et: EdgeTimings) -> Graph:
    """Build (station, line) node graph with travel + transfer edges."""
    nodes: List[Node] = []
    adj: Dict[Node, List[Tuple[Node, float]]] = {}

    for line, stations in LINE_NODES.items():
        for stn in stations:
            node = (stn, line)
            if node not in adj:
                nodes.append(node)
                adj[node] = []

    # Travel edges (adjacent stations same line)
    for line, stations in LINE_NODES.items():
        for i in range(len(stations) - 1):
            a, b = stations[i], stations[i + 1]
            na, nb = (a, line), (b, line)
            w = _edge_time(et, a, b, line)
            adj[na].append((nb, w))
            adj[nb].append((na, w))

    # Transfer edges (same station, different lines)
    station_lines = get_station_lines()
    for stn, lines in station_lines.items():
        for i, la in enumerate(lines):
            for lb in lines[i + 1:]:
                na, nb = (stn, la), (stn, lb)
                w = _transfer_time(et, stn, la, lb)
                adj[na].append((nb, w))
                adj[nb].append((na, w))

    # Walk edges (above-ground connections from walks.csv)
    for (fs, fl, ts, tl), w in et.walk_times.items():
        nf, nt = (fs, fl), (ts, tl)
        if nf in adj and nt in adj:
            adj[nf].append((nt, w))
            adj[nt].append((nf, w))

    return Graph(nodes=nodes, adj=adj)


# ---------------------------------------------------------------------------
# Dijkstra + APSP
# ---------------------------------------------------------------------------

def dijkstra(graph: Graph, source: Node) -> Tuple[Dict[Node, float], Dict[Node, Optional[Node]]]:
    dist: Dict[Node, float] = {n: float('inf') for n in graph.nodes}
    prev: Dict[Node, Optional[Node]] = {n: None for n in graph.nodes}
    dist[source] = 0.0
    pq = [(0.0, source)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in graph.adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    return dist, prev


def reconstruct_path(prev: Dict[Node, Optional[Node]], source: Node, target: Node) -> List[Node]:
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path if path and path[0] == source else []


def compute_apsp(graph: Graph) -> Tuple[Dict[Tuple[Node, Node], float], Dict[Node, Dict[Node, Optional[Node]]]]:
    """All-pairs shortest paths. Returns (dist_dict, prev_dict_per_source)."""
    all_dist: Dict[Tuple[Node, Node], float] = {}
    all_prev: Dict[Node, Dict[Node, Optional[Node]]] = {}
    for node in graph.nodes:
        d, p = dijkstra(graph, node)
        all_prev[node] = p
        for target, cost in d.items():
            all_dist[(node, target)] = cost
    return all_dist, all_prev


# ---------------------------------------------------------------------------
# Macro-graph (key-station reduction)
# ---------------------------------------------------------------------------

def _is_branch_line(line: str) -> bool:
    """Lines that are short dead-end branches hanging off another line."""
    return line in ('新北投線', '小碧潭')


def build_macro_graph(graph: Graph, et: EdgeTimings) -> MacroGraph:
    """
    Collapse interior-only stations into macro-edges between key stations.
    Dead-end branch lines (新北投線, 小碧潭, 中和新蘆線B) become mandatory
    round-trip costs stored in branch_costs[junction].
    """
    key_set = set(get_key_stations())
    station_lines = get_station_lines()

    macro_edges: List[MacroEdge] = []
    branch_costs: Dict[str, float] = {}
    branch_interiors: Dict[str, List[str]] = {}

    # Identify branch lines: lines that have exactly ONE transfer station in
    # total (which must be one of its endpoints). These are true dead-end
    # branches that require a round-trip from the junction.
    # Main lines have multiple transfer stations; branches have exactly one.
    transfers = set(get_transfer_stations().keys())
    branch_lines = {}
    for line, stations in LINE_NODES.items():
        transfer_count = sum(1 for s in stations if s in transfers)
        if transfer_count == 1:
            # The one transfer station is the junction
            junction = next(s for s in stations if s in transfers)
            # The terminus is the far end (the non-junction endpoint)
            terminus = stations[-1] if stations[0] == junction else stations[0]
            branch_lines[line] = (junction, terminus, stations)

    # Build macro-edges for non-branch lines
    for line, stations in LINE_NODES.items():
        if line in branch_lines:
            continue

        seg_start_idx = 0
        seg_start_stn = stations[0]

        for i in range(1, len(stations)):
            stn = stations[i]
            if stn in key_set or i == len(stations) - 1:
                # Compute segment cost
                cost = sum(
                    _edge_time(et, stations[j], stations[j + 1], line)
                    for j in range(seg_start_idx, i)
                )
                intermediates = stations[seg_start_idx + 1:i]
                me = MacroEdge(
                    from_key=seg_start_stn,
                    to_key=stn,
                    line=line,
                    weight=cost,
                    intermediates=intermediates,
                )
                macro_edges.append(me)
                seg_start_idx = i
                seg_start_stn = stn

    # Handle branch lines: compute round-trip cost from junction
    for line, (junction, terminus, stations) in branch_lines.items():
        # Find which end is the junction
        if stations[0] == junction:
            branch_seq = stations  # junction is first
        else:
            branch_seq = list(reversed(stations))  # junction is last → reverse

        # Cost from junction to terminus
        one_way = sum(
            _edge_time(et, branch_seq[j], branch_seq[j + 1], line)
            for j in range(len(branch_seq) - 1)
        )
        round_trip = one_way * 2
        branch_costs[junction] = branch_costs.get(junction, 0) + round_trip
        # Interior stations of this branch (everything except the junction)
        interiors = branch_seq[1:]  # from junction outward, not including junction
        branch_interiors[junction] = branch_interiors.get(junction, []) + interiors

    # Special: 中和新蘆線B merges into A at 大橋頭; B is a dead-end branch
    # (This is already handled above via the branch_lines detection.)

    # Build macro adjacency
    macro_adj: Dict[str, List[Tuple[str, float]]] = {}
    all_key = set()
    for me in macro_edges:
        all_key.add(me.from_key)
        all_key.add(me.to_key)
        macro_adj.setdefault(me.from_key, []).append((me.to_key, me.weight))
        macro_adj.setdefault(me.to_key, []).append((me.from_key, me.weight))

    key_stations = sorted(all_key)
    # Add branch junctions to key_stations if not already there
    for j in branch_costs:
        if j not in all_key:
            key_stations.append(j)
            all_key.add(j)

    return MacroGraph(
        key_stations=key_stations,
        macro_adj=macro_adj,
        macro_edges=macro_edges,
        branch_costs=branch_costs,
        branch_interiors=branch_interiors,
    )


# ---------------------------------------------------------------------------
# Macro APSP (Dijkstra on the macro-graph)
# ---------------------------------------------------------------------------

def macro_dijkstra(macro_graph: MacroGraph, source: str) -> Dict[str, float]:
    dist = {k: float('inf') for k in macro_graph.key_stations}
    dist[source] = 0.0
    pq = [(0.0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in macro_graph.macro_adj.get(u, []):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


def macro_dijkstra_full(macro_graph: MacroGraph, source: str
                         ) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
    dist = {k: float('inf') for k in macro_graph.key_stations}
    prev: Dict[str, Optional[str]] = {k: None for k in macro_graph.key_stations}
    dist[source] = 0.0
    pq = [(0.0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in macro_graph.macro_adj.get(u, []):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    return dist, prev


def compute_macro_apsp(macro_graph: MacroGraph
                        ) -> Tuple[Dict[Tuple[str, str], float], Dict[str, Dict[str, Optional[str]]]]:
    """Return (dist_dict, prev_dict_per_source) for the macro-graph."""
    all_dist: Dict[Tuple[str, str], float] = {}
    all_prev: Dict[str, Dict[str, Optional[str]]] = {}
    for k in macro_graph.key_stations:
        d, p = macro_dijkstra_full(macro_graph, k)
        all_prev[k] = p
        for t, cost in d.items():
            all_dist[(k, t)] = cost
    return all_dist, all_prev


def reconstruct_macro_path(all_prev: Dict[str, Dict[str, Optional[str]]],
                            source: str, target: str) -> List[str]:
    """Reconstruct key-station path from source to target using all_prev."""
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = all_prev[source][cur]
    path.reverse()
    return path if path and path[0] == source else []
