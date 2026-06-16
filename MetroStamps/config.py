DEFAULT_EDGE_TIME = 1      # cost between adjacent stations (same line)
DEFAULT_TRANSFER_TIME = 2  # cost to change lines at a transfer station
TOP_N_PATHS = 3
RANDOM_STARTS = 200        # random restarts for the TSP heuristic

# Default trip start
DEFAULT_START_STATION = '象山'
DEFAULT_START_TIME = '06:00'

# Default timetable values
DEFAULT_FREQUENCY = 6       # minutes between trains (most lines)
BRANCH_FREQUENCY = 10       # minutes between trains on short branch lines
DEFAULT_FIRST_TRAIN = '06:00'
DEFAULT_LAST_TRAIN = '23:59'

# Branch lines that run on a different frequency
BRANCH_LINE_FREQUENCY = {
    '新北投線': 10,
    '小碧潭': 10,
}

# Transfers where you physically STAY ON the same train (no boarding wait).
# The train from 蘆洲 continues through 大橋頭 onto 中和新蘆線A without stopping.
SAME_TRAIN_TRANSFERS = {
    ('大橋頭', '中和新蘆線A', '中和新蘆線B'),
    ('大橋頭', '中和新蘆線B', '中和新蘆線A'),
}

# Transfer walk-times that differ from DEFAULT_TRANSFER_TIME.
# Format: (station, line_a, line_b) -> minutes  (applied in both directions).
SPECIAL_TRANSFER_TIMES = {
    ('大橋頭', '中和新蘆線A', '中和新蘆線B'): 0,
}
