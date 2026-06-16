# go-backend

The Hanamikoji game engine. Manages all game state and turn flow; knows nothing about ML.

## Build & run

```bash
go build -o hanamikoji .
./hanamikoji
```

## Structure

| File | Contents |
|---|---|
| `main.go` | `Game` struct, round/turn loop, initialization |
| `cards.go` | `Suit`, `Geisha`, `Deck` types and constants |
| `actions.go` | `Action` metadata, `ActionName` constants |
| `player.go` | `Player` struct, decision methods, JSON I/O |
| `public_info.go` | `Observation`, `StepRequest`, `PendingAction` |
| `gameStates.go` | `StepChooseAction`, `StepChooseCards`, `StepOpponentResponse`, `StepResolve` |
| `cli/cli.go` | Writes JSON to stdout, reads one line from stdin |

## Communication protocol

At each decision point the engine writes a `StepRequest` JSON object (one line) to stdout and blocks reading one line from stdin. The response format depends on the step:

| `step` | Response |
|---|---|
| `"ChooseAction"` | JSON string — one of the `valid_actions` |
| `"ChooseCards"` | JSON array of suit name strings, length == `n_cards_to_choose` |
| `"OpponentResponse"` | JSON integer `0` or `1` |
