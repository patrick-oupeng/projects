# python-ml

The ML agent for Hanamikoji. Reads `StepRequest` JSON from stdin, outputs decisions as JSON.

## Run

```bash
python3 agent.py
```

It reads lines from stdin indefinitely, one decision per line out.

## agent.py

Currently stubs — returns the first valid option for every decision. Replace the three functions to plug in a real model:

```python
def choose_action(obs, valid_actions) -> str:   # return one of valid_actions
def choose_cards(obs, n) -> list[str]:           # return n suit names from obs["MyHand"]
def respond(obs) -> int:                         # return 0 or 1
```

## ML plan

See `obsidian/action-system-design.md` — Step 3 covers the full training setup:

- **Environment**: [PettingZoo](https://pettingzoo.farama.org/) multi-agent env wrapping the Go engine
- **Algorithm**: [MaskablePPO](https://sb3-contrib.readthedocs.io/en/master/modules/ppo_mask.html) from `sb3-contrib` (handles variable action spaces cleanly)
- **Training**: self-play, reward `+1/-1` per round, shaped reward optional
- **Deployment**: export to ONNX, load in Go via `onnxruntime-go` to eliminate the Python subprocess at inference time
