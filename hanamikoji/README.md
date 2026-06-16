# Hanamikoji

A two-player card game engine with a Python ML training interface.

## Structure

```
go-backend/   Game engine (Go). Handles all rules, state, and turn flow.
python-ml/    ML agent (Python). Receives observations, outputs decisions.
```

## How they connect

Go runs the game loop. At each decision point it serializes a `StepRequest` to JSON, writes it to stdout, and reads one JSON line back from stdin. Python sits on the other end of that pipe.

```
go-backend binary
    stdout → JSON observation (StepRequest)
    stdin  ← JSON decision
python-ml/agent.py
```

To wire them together, pipe Go's output into Python and Python's output back:

```bash
cd go-backend && go build -o ../hanamikoji-engine .
./hanamikoji-engine | python3 python-ml/agent.py | ./hanamikoji-engine
```

(A proper two-way pipe needs a wrapper script or named pipes — the above is illustrative.)

## Design doc

See `obsidian/action-system-design.md` for the full architecture, action system, and ML training plan.
