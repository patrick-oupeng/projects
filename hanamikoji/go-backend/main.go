package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"math/rand"
	"os"
)

const (
	points_to_win  = 11
	geishas_to_win = 4
	starting_cards = 6
	maxRounds      = 50
)

type Game struct {
	player1           *Player
	player2           *Player
	startingPlayerPos PlayerPosition
	currentPlayerPos  PlayerPosition
	deck              Deck
	playingField      []*Geisha
	pendingAction     *PendingAction
	debug             io.Writer // receives human-readable output; use io.Discard in engine mode
}

func (g *Game) playerFromPosition(pos PlayerPosition) *Player {
	if pos == Player1Position {
		return g.player1
	}
	return g.player2
}

func (g *Game) getCurrentPlayer() *Player {
	return g.playerFromPosition(g.currentPlayerPos)
}

func (g *Game) getOpponent() *Player {
	if g.currentPlayerPos == Player1Position {
		return g.playerFromPosition(Player2Position)
	}
	return g.playerFromPosition(Player1Position)
}

type WinStatus int

const (
	NoWinner   WinStatus = 0
	Player1Win WinStatus = 1
	Player2Win WinStatus = 2
)

func (g *Game) observationFor(player *Player) (Observation, error) {
	opponent := g.player1
	if player.playerPosition == Player1Position {
		opponent = g.player2
	}
	var offeredGift, offeredCompetition []Suit
	if g.pendingAction != nil {
		offeredGift = g.pendingAction.chosenGift
		offeredCompetition = g.pendingAction.chosenCompetition
	}
	return Observation{
		ActivePlayer:       int(player.playerPosition),
		PlayingField:       g.playingField,
		MyActions:          player.actions,
		OpponentActions:    opponent.actions,
		MySavedCard:        player.savedCard,
		MyDiscardedCards:   player.thrownCards,
		MyHand:             player.cards,
		OfferedGift:        offeredGift,
		OfferedCompetition: offeredCompetition,
	}, nil
}

// Card is played to the playing field
func (g *Game) playCard(player *Player, card Suit) error {
	for _, geisha := range g.playingField {
		if geisha.Suit == card {
			if player.playerPosition == Player1Position {
				geisha.Player1Cards += 1
			} else {
				geisha.Player2Cards += 1
			}
			return nil
		}
	}
	return fmt.Errorf("Card %s does not match any geisha on the playing field", card)
}

func (g *Game) playMultipleCards(player *Player, cards []Suit) error {
	for _, c := range cards {
		err := g.playCard(player, c)
		if err != nil {
			return err
		}
	}
	return nil
}

func (g *Game) playSecrets() error {
	err := g.playCard(g.player1, g.player1.savedCard)
	if err != nil {
		return err
	}
	err = g.playCard(g.player2, g.player2.savedCard)
	if err != nil {
		return err
	}
	return nil
}

func (g *Game) playRound() error {
	for {
		if g.ShouldEndRound() {
			return nil
		}
		currentPlayer := g.getCurrentPlayer()

		if err := g.drawOne(currentPlayer); err != nil {
			return err
		}

		gameState, err := g.observationFor(currentPlayer)
		if err != nil {
			return err
		}
		opponent := g.getOpponent()

		err = g.StepChooseAction(currentPlayer, gameState)
		if err != nil {
			return err
		}
		// the Observation needs to be updated now that the action is selected
		gameState, err = g.observationFor(currentPlayer)
		if err != nil {
			return err
		}

		err = g.StepChooseCards(currentPlayer, gameState)
		if err != nil {
			return err
		}
		fmt.Fprintf(g.debug, "  P%d plays %s\n", currentPlayer.playerPosition+1, g.pendingAction.action.actionName)

		if g.pendingAction.action.requiresOpponentResponse {
			opponentObservation, err := g.observationFor(opponent)
			if err != nil {
				return err
			}
			err = g.StepOpponentResponse(opponent, opponentObservation)
			if err != nil {
				return err
			}
			fmt.Fprintf(g.debug, "  P%d responds: choice %d\n", opponent.playerPosition+1, g.pendingAction.opponentChoice)
		}

		err = g.StepResolve(currentPlayer, opponent)
		if err != nil {
			return err
		}

		g.currentPlayerPos = (g.currentPlayerPos + 1) % 2
	}
}

func (g *Game) endRound() (WinStatus, error) {
	err := g.playSecrets()
	if err != nil {
		return NoWinner, err
	}
	newPlayer1Points := 0
	newPlayer2Points := 0
	newPlayer1Geishas := 0
	newPlayer2Geishas := 0
	for _, geisha := range g.playingField {
		if geisha.Player1Cards > geisha.Player2Cards {
			geisha.MarkerPosition = Player1
			newPlayer1Points += geisha.Points
			newPlayer1Geishas += 1
		} else if geisha.Player2Cards > geisha.Player1Cards {
			newPlayer2Points += geisha.Points
			newPlayer2Geishas += 1
		}
	}
	g.player1.currentPoints = newPlayer1Points
	g.player1.currentGeishas = newPlayer1Geishas
	g.player2.currentPoints = newPlayer2Points
	g.player2.currentGeishas = newPlayer2Geishas
	if g.player1.currentPoints >= points_to_win || g.player1.currentGeishas >= geishas_to_win {
		return Player1Win, nil
	} else if g.player2.currentPoints >= points_to_win || g.player2.currentGeishas >= geishas_to_win {
		return Player2Win, nil
	} else {
		return NoWinner, nil
	}
}

func (g *Game) drawOne(player *Player) error {
	card, err := g.deck.DrawOne()
	if err != nil {
		return err
	}
	player.cards = append(player.cards, card)
	return nil
}

func (g *Game) ResetForNextRound() error {
	g.deck = shuffleDeck(makeDeck())
	err := g.player1.resetForNextRound(&g.deck)
	if err != nil {
		return err
	}
	err = g.player2.resetForNextRound(&g.deck)
	if err != nil {
		return err
	}
	for i := range g.playingField {
		g.playingField[i].Player1Cards = 0
		g.playingField[i].Player2Cards = 0
	}
	// alternate who starts for each round
	g.startingPlayerPos = (g.startingPlayerPos + 1) % 2
	g.currentPlayerPos = g.startingPlayerPos
	return nil
}

func (g *Game) ShouldEndRound() bool {
	for _, taken := range g.player1.actions {
		if !taken {
			return false
		}
	}
	for _, taken := range g.player2.actions {
		if !taken {
			return false
		}
	}
	return true
}

func InitializeGame(agent1, agent2 Agent, debug io.Writer) (*Game, error) {
	deck := shuffleDeck(makeDeck())

	player1Cards, err := deck.DrawCards(starting_cards)
	if err != nil {
		return nil, fmt.Errorf("failed to draw cards for player 1: %v", err)
	}
	player2Cards, err := deck.DrawCards(starting_cards)
	if err != nil {
		return nil, fmt.Errorf("failed to draw cards for player 2: %v", err)
	}

	player1 := &Player{
		playerPosition: Player1Position,
		actions:        defaultActions(),
		cards:          player1Cards,
		agent:          agent1,
	}

	player2 := &Player{
		playerPosition: Player2Position,
		actions:        defaultActions(),
		cards:          player2Cards,
		agent:          agent2,
	}

	startingPlayer := Player1Position
	if rand.Intn(2) == int(Player2Position) {
		startingPlayer = Player2Position
	}

	return &Game{
		player1:           player1,
		player2:           player2,
		deck:              deck,
		playingField:      makePlayingField(),
		startingPlayerPos: startingPlayer,
		currentPlayerPos:  startingPlayer,
		pendingAction:     nil,
		debug:             debug,
	}, nil
}

func (g *Game) runGame() (WinStatus, error) {
	var status WinStatus
	var err error
	for roundCounter := 1; roundCounter < maxRounds; roundCounter++ {
		fmt.Fprintf(g.debug, "=== Round %d ===\n", roundCounter)
		if err = g.playRound(); err != nil {
			return NoWinner, err
		}
		status, err = g.endRound()
		if err != nil {
			return NoWinner, err
		}
		fmt.Fprintf(g.debug, "  P1: %d pts / %d geishas  |  P2: %d pts / %d geishas\n",
			g.player1.currentPoints, g.player1.currentGeishas,
			g.player2.currentPoints, g.player2.currentGeishas)
		if status != NoWinner {
			fmt.Fprintf(g.debug, "Winner: P%d\n", int(status))
			return status, nil
		}
		if err = g.ResetForNextRound(); err != nil {
			return NoWinner, err
		}
	}
	fmt.Fprintf(g.debug, "hit max rounds with no winner\n")
	if g.player1.currentPoints > g.player2.currentPoints {
		return Player1Win, nil
	} else if g.player2.currentPoints > g.player1.currentPoints {
		return Player2Win, nil
	} else if g.player1.currentGeishas > g.player2.currentGeishas {
		return Player1Win, nil
	}
	return Player2Win, nil
}

func winStatusToPlayerIndex(s WinStatus) int {
	if s == Player1Win {
		return 0
	}
	if s == Player2Win {
		return 1
	}
	return -1
}

func main() {
	engineMode := flag.Bool("engine", false, "run in engine mode: JSON protocol over stdin/stdout for Python ML training")
	flag.Parse()

	var agent1, agent2 Agent
	var debug io.Writer

	if *engineMode {
		cli := NewCLIAgent()
		agent1, agent2 = cli, cli
		debug = os.Stderr
	} else {
		agent1, agent2 = &RandomAgent{}, &RandomAgent{}
		debug = os.Stdout
	}

	game, err := InitializeGame(agent1, agent2, debug)
	if err != nil {
		panic(fmt.Sprintf("Failed to initialize game: %v", err))
	}

	status, err := game.runGame()
	if err != nil {
		panic(fmt.Sprintf("runGame: %v", err))
	}

	if *engineMode {
		result := GameResult{Done: true, Winner: winStatusToPlayerIndex(status)}
		data, _ := json.Marshal(result)
		fmt.Fprintln(os.Stdout, string(data))
	}
}
