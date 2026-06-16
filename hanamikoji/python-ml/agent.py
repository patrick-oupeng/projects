import sys
import json


def choose_action(obs: dict, valid_actions: list[str]) -> str:
    # stub: pick first valid action
    return valid_actions[0]


def choose_cards(obs: dict, n: int) -> list[str]:
    # stub: pick first n cards from hand
    return obs["MyHand"][:n]


def respond(obs: dict) -> int:
    # stub: always pick option 0
    return 0


def decide(req: dict) -> object:
    step = req["step"]
    obs = req["observation"]

    if step == "ChooseAction":
        return choose_action(obs, req["valid_actions"])
    elif step == "ChooseCards":
        return choose_cards(obs, req["n_cards_to_choose"])
    elif step == "OpponentResponse":
        return respond(obs)
    else:
        raise ValueError(f"unknown step: {step}")


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        req = json.loads(line)
        result = decide(req)
        print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
