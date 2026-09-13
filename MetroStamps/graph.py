'''
Build the graph from full_station_list.json and full_transfers_list.json.
TODO later: add manual transfers, like Guangci-Houshanpi.
TODO later later: add transfer times.
'''

ALL_STATIONS_JSON = "full_station_list.json"
ALL_TRANSFERS_JSON = "full_transfers_list.json"
LINE_PREFIXES = ["BL", "Y", "G", "R", "O", "BR"]

import json
import networkx as nx 


class MetroGraph:
    def __init__(self):
        self.G = nx.DiGraph()
    
    def add_station(self, station_id, station_name_en, station_name_zh):
        """Add a station node"""
        line = ""
        for l in LINE_PREFIXES:
            if station_id.startswith(l):
                color = l
        if line = "":
            return -1
        attrs = {
            'name': name,
            'station_id': station_id,
            'line': color
        }
        self.G.add_node(station_id, **attrs)
    
    def add_transfer(self, from_station_id, to_station_id, transfer_time):
        # TODO
        # Note that forks like Xinbeitou/Daqiaotou/Qizhang are transfers to themself
        return
    
    def add_edge(self, from_station_id, to_station_id, line, travel_time):
        """
        Add an edge representing track between two stations.
        This is one-directional, so it needs to be called twice with from/to swapped.
        """
        self.G.add_edge(from_station_id, to_station_id, line, travel_time)
    

def parse_station_list(full_station_json=ALL_STATIONS_JSON):
    
    



    