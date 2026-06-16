"""
One-shot prediction from a raw game state.

Usage:
    python predict.py --obs obs.json --step ChooseAction
    python predict.py --obs obs.json --step ChooseCards --n 3
    python predict.py --obs obs.json --step OpponentResponse

obs.json should match the Observation shape from Go:
{
    "ActivePlayer": 0,
    "PlayingField": [
        {"Suit": "Flute",    "Points": 2, "Player1Cards": 0, "Player2Cards": 1, "MarkerPosition": 0},
        {"Suit": "Fan",      "Points": 2, "Player1Cards": 1, "Player2Cards": 0, "MarkerPosition": 0},
        {"Suit": "Scroll",   "Points": 2, "Player1Cards": 0, "Player2Cards": 0, "MarkerPosition": 0},
        {"Suit": "Parasol",  "Points": 3, "Player1Cards": 0, "Player2Cards": 0, "MarkerPosition": 0},
        {"Suit": "Shamisen", "Points": 3, "Player1Cards": 0, "Player2Cards": 0, "MarkerPosition": 0},
        {"Suit": "TeaSet",   "Points": 4, "Player1Cards": 0, "Player2Cards": 0, "MarkerPosition": 0},
        {"Suit": "HairPin",  "Points": 5, "Player1Cards": 0, "Player2Cards": 0, "MarkerPosition": 0}
    ],
    "MyActions":       {"Secret": false, "Discard": false, "Gift": false, "Competition": false},
    "OpponentActions": {"Secret": false, "Discard": false, "Gift": false, "Competition": false},
    "MyHand":          ["TeaSet", "HairPin", "Parasol"],
    "MyDiscardedCards": [],
    "OfferedGift":        null,
    "OfferedCompetition": null
}
"""
import argparse
import json
from itertools import combinations

import numpy as np
from sb3_contrib import MaskablePPO

from features import ACTIONS, OBS_SIZE, encode
from env import MAX_ACTIONS


def build_req(obs: dict, step: str, n_cards: int, valid_actions: list[str]) -> dict:
    return {
        "step": step,
        "observation": obs,
        "valid_actions": valid_actions,
        "n_cards_to_choose": n_cards,
    }


def compute_legal(req: dict) -> list[int]:
    step = req["step"]
    obs = req["observation"]
    if step == "ChooseAction":
        return [ACTIONS.index(a) for a in req["valid_actions"]]
    elif step == "ChooseCards":
        n = req["n_cards_to_choose"]
        count = len(list(combinations(range(len(obs["MyHand"])), n)))
        return list(range(count))
    elif step == "OpponentResponse":
        offered = obs.get("OfferedGift") or []
        return list(range(len(offered) if offered else 2))
    return []


def decode(index: int, req: dict):
    step = req["step"]
    obs = req["observation"]
    if step == "ChooseAction":
        return ACTIONS[index]
    elif step == "ChooseCards":
        n = req["n_cards_to_choose"]
        hand = obs["MyHand"]
        combos = list(combinations(range(len(hand)), n))
        return [hand[i] for i in combos[index]]
    elif step == "OpponentResponse":
        offered = obs.get("OfferedGift") or obs.get("OfferedCompetition") or []
        return f"pick index {index}" + (f" ({offered[index]})" if index < len(offered) else "")


def main():
    parser = argparse.ArgumentParser(description="Get model prediction for a single game state")
    parser.add_argument("--obs", required=True, help="Path to observation JSON file")
    parser.add_argument("--model", default="hanamikoji_agent", help="Path to saved model (no .zip)")
    parser.add_argument(
        "--step",
        default="ChooseAction",
        choices=["ChooseAction", "ChooseCards", "OpponentResponse"],
    )
    parser.add_argument("--n", type=int, default=1, help="Cards to choose (ChooseCards only)")
    parser.add_argument(
        "--valid-actions",
        nargs="+",
        default=["Secret", "Discard", "Gift", "Competition"],
        help="Available actions (ChooseAction only)",
    )
    parser.add_argument("--top", type=int, default=1, help="Show top N recommendations")
    args = parser.parse_args()

    obs = json.load(open(args.obs))
    req = build_req(obs, args.step, args.n, args.valid_actions)

    model = MaskablePPO.load(args.model)

    encoded = encode(req)
    legal = compute_legal(req)

    mask = np.zeros(MAX_ACTIONS, dtype=np.int8)
    for i in legal:
        if i < MAX_ACTIONS:
            mask[i] = 1

    if args.top == 1:
        action, _ = model.predict(encoded, action_masks=mask, deterministic=True)
        print(decode(int(action), req))
    else:
        # get raw logits and show top N legal moves ranked by confidence
        import torch
        obs_tensor = torch.tensor(encoded).unsqueeze(0)
        with torch.no_grad():
            dist = model.policy.get_distribution(obs_tensor)
            logits = dist.distribution.logits.squeeze(0).numpy()

        ranked = sorted(legal, key=lambda i: logits[i], reverse=True)
        print(f"Top {args.top} recommendations:")
        for rank, idx in enumerate(ranked[:args.top], 1):
            print(f"  {rank}. {decode(idx, req)}  (logit {logits[idx]:.2f})")


if __name__ == "__main__":
    main()
