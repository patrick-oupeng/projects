import numpy as np

SUITS = ["Flute", "Fan", "Scroll", "Parasol", "Shamisen", "TeaSet", "HairPin"]
ACTIONS = ["Secret", "Discard", "Gift", "Competition"]
SUIT_INDEX = {s: i for i, s in enumerate(SUITS)}
STEPS = ["ChooseAction", "ChooseCards", "OpponentResponse"]

OBS_SIZE = 53  # 21 field + 4 my_actions + 4 opp_actions + 7 hand + 7 discard + 7 offered + 3 step


def encode(req: dict) -> np.ndarray:
    obs = req["observation"]
    features = []

    # Playing field: 7 geishas × 3 values = 21
    for geisha in obs["PlayingField"]:
        features.append(float(geisha["Player1Cards"]))
        features.append(float(geisha["Player2Cards"]))
        features.append(float(geisha["MarkerPosition"]))

    # My actions still available: 4 (1 = available)
    for a in ACTIONS:
        features.append(0.0 if obs["MyActions"][a] else 1.0)

    # Opponent actions still available: 4
    for a in ACTIONS:
        features.append(0.0 if obs["OpponentActions"][a] else 1.0)

    # My hand: suit counts = 7
    hand_counts = [0] * len(SUITS)
    for card in obs["MyHand"]:
        hand_counts[SUIT_INDEX[card]] += 1
    features.extend(map(float, hand_counts))

    # My discarded: suit counts = 7
    discard_counts = [0] * len(SUITS)
    for card in (obs["MyDiscardedCards"] or []):
        discard_counts[SUIT_INDEX[card]] += 1
    features.extend(map(float, discard_counts))

    # Offered cards (gift or competition, whichever is set): suit counts = 7
    offered_counts = [0] * len(SUITS)
    offered = obs.get("OfferedGift") or obs.get("OfferedCompetition") or []
    for card in offered:
        offered_counts[SUIT_INDEX[card]] += 1
    features.extend(map(float, offered_counts))

    # Step one-hot: 3
    step = req["step"]
    features.extend([1.0 if step == s else 0.0 for s in STEPS])

    assert len(features) == OBS_SIZE, f"expected {OBS_SIZE} features, got {len(features)}"
    return np.array(features, dtype=np.float32)
