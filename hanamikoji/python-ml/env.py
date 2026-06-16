import json
import subprocess
from itertools import combinations
from pathlib import Path

import numpy as np
import gymnasium

from features import ACTIONS, OBS_SIZE, encode

ENGINE_PATH = str(Path(__file__).parent.parent / "hanamikoji-engine")

# Largest legal action count at any step:
#   ChooseCards Gift/Competition: C(7,3) = C(7,4) = 35
#   ChooseAction: 4, OpponentResponse: 3
MAX_ACTIONS = 35


class HanamikojiEnv(gymnasium.Env):
    """
    Single-agent self-play env. The model plays as whoever's turn it is at each
    step — observation is always from the active player's perspective, so one
    policy works for both sides.
    """

    metadata = {"render_modes": []}

    def __init__(self):
        super().__init__()
        self.observation_space = gymnasium.spaces.Box(
            0.0, 10.0, shape=(OBS_SIZE,), dtype=np.float32
        )
        self.action_space = gymnasium.spaces.Discrete(MAX_ACTIONS)
        self._proc = None
        self._current_req = None
        self._legal: list[int] = []

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()

        self._proc = subprocess.Popen(
            [ENGINE_PATH, "-engine"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        self._current_req = self._read()
        self._legal = self._compute_legal(self._current_req)
        return encode(self._current_req), {}

    def step(self, action: int):
        decision = self._decode(action, self._current_req)
        self._write(decision)

        line = self._proc.stdout.readline()
        if not line:
            # Go closed stdout without sending a result — treat as tie
            return np.zeros(OBS_SIZE, dtype=np.float32), 0.0, True, False, {}

        msg = json.loads(line)

        if msg.get("done"):
            winner = msg["winner"]
            active = self._current_req["observation"]["ActivePlayer"]
            # reward is from the perspective of whoever just acted
            if winner == active:
                reward = 1.0
            elif winner == -1:
                reward = 0.0
            else:
                reward = -1.0
            return np.zeros(OBS_SIZE, dtype=np.float32), reward, True, False, {}

        self._current_req = msg
        self._legal = self._compute_legal(self._current_req)
        return encode(self._current_req), 0.0, False, False, {}

    def action_mask(self) -> np.ndarray:
        mask = np.zeros(MAX_ACTIONS, dtype=np.int8)
        for i in self._legal:
            if i < MAX_ACTIONS:
                mask[i] = 1
        return mask

    def _read(self) -> dict:
        return json.loads(self._proc.stdout.readline())

    def _write(self, decision):
        self._proc.stdin.write(json.dumps(decision) + "\n")
        self._proc.stdin.flush()

    def _compute_legal(self, req: dict) -> list[int]:
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

    def _decode(self, index, req: dict):
        index = int(index)  # numpy int64 → Python int so json.dumps works
        step = req["step"]
        obs = req["observation"]
        if step == "ChooseAction":
            return ACTIONS[index]
        elif step == "ChooseCards":
            n = req["n_cards_to_choose"]
            hand = obs["MyHand"]
            combos = list(combinations(range(len(hand)), n))
            positions = combos[index]
            return [hand[i] for i in positions]
        elif step == "OpponentResponse":
            return index
        raise ValueError(f"unknown step: {step}")

    def close(self):
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
